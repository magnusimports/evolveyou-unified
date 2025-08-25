"""
Middleware de rate limiting
"""

import time
from typing import Dict, Any, Callable
from functools import wraps
from fastapi import HTTPException, Request, status
import structlog

from config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Cache em memória para rate limiting (em produção usar Redis)
rate_limit_cache: Dict[str, Dict[str, Any]] = {}

def rate_limit(requests: int = None, window: int = None):
    """
    Decorator para rate limiting
    
    Args:
        requests: Número máximo de requests
        window: Janela de tempo em segundos
    """
    max_requests = requests or settings.rate_limit_requests
    time_window = window or settings.rate_limit_window
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair request do contexto
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Se não conseguir extrair request, prosseguir sem rate limit
                return await func(*args, **kwargs)
            
            # Identificar cliente (IP + User-Agent para maior precisão)
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "")
            client_id = f"{client_ip}:{hash(user_agent)}"
            
            # Verificar rate limit
            current_time = time.time()
            
            if client_id not in rate_limit_cache:
                rate_limit_cache[client_id] = {
                    "requests": [],
                    "blocked_until": 0
                }
            
            client_data = rate_limit_cache[client_id]
            
            # Verificar se ainda está bloqueado
            if current_time < client_data["blocked_until"]:
                remaining_time = int(client_data["blocked_until"] - current_time)
                logger.warning(
                    "Rate limit ativo",
                    client_id=client_id,
                    remaining_time=remaining_time
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Muitas tentativas. Tente novamente em {remaining_time} segundos.",
                    headers={"Retry-After": str(remaining_time)}
                )
            
            # Limpar requests antigos
            cutoff_time = current_time - time_window
            client_data["requests"] = [
                req_time for req_time in client_data["requests"]
                if req_time > cutoff_time
            ]
            
            # Verificar se excedeu o limite
            if len(client_data["requests"]) >= max_requests:
                # Bloquear por tempo adicional
                client_data["blocked_until"] = current_time + time_window
                
                logger.warning(
                    "Rate limit excedido",
                    client_id=client_id,
                    requests_count=len(client_data["requests"]),
                    max_requests=max_requests,
                    window=time_window
                )
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Limite de {max_requests} requests por {time_window} segundos excedido.",
                    headers={"Retry-After": str(time_window)}
                )
            
            # Registrar request atual
            client_data["requests"].append(current_time)
            
            # Adicionar headers informativos
            remaining_requests = max_requests - len(client_data["requests"])
            
            # Executar função original
            result = await func(*args, **kwargs)
            
            # Se o resultado for uma Response, adicionar headers
            if hasattr(result, "headers"):
                result.headers["X-RateLimit-Limit"] = str(max_requests)
                result.headers["X-RateLimit-Remaining"] = str(remaining_requests)
                result.headers["X-RateLimit-Reset"] = str(int(current_time + time_window))
            
            return result
        
        return wrapper
    return decorator

def cleanup_rate_limit_cache():
    """Limpar cache de rate limiting (executar periodicamente)"""
    current_time = time.time()
    expired_clients = []
    
    for client_id, client_data in rate_limit_cache.items():
        # Remover clientes que não fazem requests há muito tempo
        if (not client_data["requests"] and 
            current_time > client_data.get("blocked_until", 0) + 3600):  # 1 hora
            expired_clients.append(client_id)
    
    for client_id in expired_clients:
        del rate_limit_cache[client_id]
    
    logger.info("Cache de rate limiting limpo", removed_clients=len(expired_clients))

# Rate limiting específico para endpoints sensíveis
def strict_rate_limit(requests: int = 3, window: int = 300):
    """Rate limiting mais restritivo para endpoints sensíveis"""
    return rate_limit(requests, window)

def auth_rate_limit(requests: int = 5, window: int = 300):
    """Rate limiting para endpoints de autenticação"""
    return rate_limit(requests, window)


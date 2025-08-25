"""
Middleware de logging estruturado
"""

import sys
import logging
from typing import Dict, Any
import structlog
from structlog.stdlib import LoggerFactory

from config.settings import get_settings

settings = get_settings()

def setup_logging():
    """Configurar logging estruturado"""
    
    # Configurar processadores do structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configurar structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configurar logging padrão
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper())
    )

def get_request_logger(request_id: str = None, user_id: str = None) -> structlog.BoundLogger:
    """Obter logger com contexto de request"""
    logger = structlog.get_logger()
    
    context = {}
    if request_id:
        context["request_id"] = request_id
    if user_id:
        context["user_id"] = user_id
    
    return logger.bind(**context)

class LoggingMiddleware:
    """Middleware para logging de requests"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Gerar ID único para o request
        import uuid
        request_id = str(uuid.uuid4())
        
        # Adicionar ao scope
        scope["request_id"] = request_id
        
        # Logger com contexto
        logger = get_request_logger(request_id)
        
        # Log do início do request
        logger.info(
            "Request iniciado",
            method=scope["method"],
            path=scope["path"],
            query_string=scope.get("query_string", b"").decode(),
            client=scope.get("client", ["unknown", 0])[0]
        )
        
        # Processar request
        await self.app(scope, receive, send)
        
        # Log do fim do request seria feito em um middleware de response
        # mas para simplicidade, vamos deixar assim


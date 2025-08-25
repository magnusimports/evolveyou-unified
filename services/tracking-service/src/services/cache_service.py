"""
Serviço de cache para otimização de performance
"""

import json
import asyncio
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import structlog

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from config.settings import get_settings

logger = structlog.get_logger(__name__)


class CacheService:
    """Serviço de cache com fallback para cache em memória"""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[aioredis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.use_redis = REDIS_AVAILABLE and self.settings.redis_url is not None
        self.default_ttl = self.settings.cache_ttl_seconds
        
    async def initialize(self):
        """Inicializa o serviço de cache"""
        try:
            if self.use_redis:
                # Tentar conectar ao Redis
                self.redis_client = aioredis.from_url(
                    self.settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                
                # Testar conexão
                await self.redis_client.ping()
                logger.info("Cache Redis inicializado", url=self.settings.redis_url)
            else:
                logger.info("Usando cache em memória (Redis não disponível)")
                
        except Exception as e:
            logger.warning("Falha ao conectar Redis, usando cache em memória", 
                          error=str(e))
            self.redis_client = None
            self.use_redis = False
    
    async def close(self):
        """Fecha conexões do cache"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                logger.info("Cache Redis finalizado")
        except Exception as e:
            logger.error("Erro ao finalizar cache", error=str(e))
    
    async def health_check(self) -> bool:
        """Verifica se o cache está funcionando"""
        try:
            if self.use_redis and self.redis_client:
                await self.redis_client.ping()
                return True
            else:
                # Cache em memória sempre funciona
                return True
        except Exception as e:
            logger.error("Health check do cache falhou", error=str(e))
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Any: Valor armazenado ou None se não encontrado
        """
        try:
            if self.use_redis and self.redis_client:
                # Usar Redis
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Usar cache em memória
                cache_entry = self.memory_cache.get(key)
                if cache_entry:
                    # Verificar se não expirou
                    if datetime.utcnow() < cache_entry["expires_at"]:
                        return cache_entry["value"]
                    else:
                        # Remover entrada expirada
                        del self.memory_cache[key]
            
            return None
            
        except Exception as e:
            logger.error("Erro ao obter do cache", key=key, error=str(e))
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Armazena valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl_seconds: Tempo de vida em segundos (opcional)
            
        Returns:
            bool: True se armazenado com sucesso
        """
        try:
            ttl = ttl_seconds or self.default_ttl
            
            if self.use_redis and self.redis_client:
                # Usar Redis
                await self.redis_client.setex(
                    key, 
                    ttl, 
                    json.dumps(value, default=str)
                )
            else:
                # Usar cache em memória
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
                self.memory_cache[key] = {
                    "value": value,
                    "expires_at": expires_at
                }
                
                # Limpar cache em memória se ficar muito grande
                if len(self.memory_cache) > 1000:
                    await self._cleanup_memory_cache()
            
            logger.debug("Valor armazenado no cache", key=key, ttl=ttl)
            return True
            
        except Exception as e:
            logger.error("Erro ao armazenar no cache", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Remove valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            if self.use_redis and self.redis_client:
                # Usar Redis
                await self.redis_client.delete(key)
            else:
                # Usar cache em memória
                self.memory_cache.pop(key, None)
            
            logger.debug("Valor removido do cache", key=key)
            return True
            
        except Exception as e:
            logger.error("Erro ao remover do cache", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Verifica se chave existe no cache
        
        Args:
            key: Chave do cache
            
        Returns:
            bool: True se existe
        """
        try:
            if self.use_redis and self.redis_client:
                return bool(await self.redis_client.exists(key))
            else:
                cache_entry = self.memory_cache.get(key)
                if cache_entry:
                    # Verificar se não expirou
                    return datetime.utcnow() < cache_entry["expires_at"]
                return False
                
        except Exception as e:
            logger.error("Erro ao verificar existência no cache", key=key, error=str(e))
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Remove todas as chaves que correspondem ao padrão
        
        Args:
            pattern: Padrão de chaves (ex: "user:123:*")
            
        Returns:
            int: Número de chaves removidas
        """
        try:
            count = 0
            
            if self.use_redis and self.redis_client:
                # Usar Redis
                keys = await self.redis_client.keys(pattern)
                if keys:
                    count = await self.redis_client.delete(*keys)
            else:
                # Usar cache em memória
                import fnmatch
                keys_to_remove = [
                    key for key in self.memory_cache.keys()
                    if fnmatch.fnmatch(key, pattern)
                ]
                for key in keys_to_remove:
                    del self.memory_cache[key]
                count = len(keys_to_remove)
            
            logger.info("Chaves removidas por padrão", pattern=pattern, count=count)
            return count
            
        except Exception as e:
            logger.error("Erro ao limpar por padrão", pattern=pattern, error=str(e))
            return 0
    
    async def _cleanup_memory_cache(self):
        """Limpa entradas expiradas do cache em memória"""
        try:
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if now >= entry["expires_at"]
            ]
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            logger.debug("Cache em memória limpo", expired_count=len(expired_keys))
            
        except Exception as e:
            logger.error("Erro ao limpar cache em memória", error=str(e))
    
    # Métodos específicos para o tracking service
    
    async def get_dashboard_cache(self, user_id: str, date: str) -> Optional[Dict[str, Any]]:
        """Obtém dashboard do cache"""
        key = f"dashboard:{user_id}:{date}"
        return await self.get(key)
    
    async def set_dashboard_cache(
        self, 
        user_id: str, 
        date: str, 
        dashboard_data: Dict[str, Any]
    ) -> bool:
        """Armazena dashboard no cache"""
        key = f"dashboard:{user_id}:{date}"
        # Cache de dashboard por 5 minutos
        return await self.set(key, dashboard_data, ttl_seconds=300)
    
    async def get_progress_cache(self, user_id: str, days: int) -> Optional[Dict[str, Any]]:
        """Obtém dados de progresso do cache"""
        key = f"progress:{user_id}:{days}"
        return await self.get(key)
    
    async def set_progress_cache(
        self, 
        user_id: str, 
        days: int, 
        progress_data: Dict[str, Any]
    ) -> bool:
        """Armazena dados de progresso no cache"""
        key = f"progress:{user_id}:{days}"
        # Cache de progresso por 15 minutos
        return await self.set(key, progress_data, ttl_seconds=900)
    
    async def invalidate_user_cache(self, user_id: str) -> int:
        """Invalida todo o cache de um usuário"""
        pattern = f"*:{user_id}:*"
        return await self.clear_pattern(pattern)
    
    async def get_service_data_cache(
        self, 
        service: str, 
        endpoint: str, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Obtém dados de serviço do cache"""
        key = f"service:{service}:{endpoint}:{user_id}"
        return await self.get(key)
    
    async def set_service_data_cache(
        self,
        service: str,
        endpoint: str,
        user_id: str,
        data: Dict[str, Any],
        ttl_seconds: int = 300
    ) -> bool:
        """Armazena dados de serviço no cache"""
        key = f"service:{service}:{endpoint}:{user_id}"
        return await self.set(key, data, ttl_seconds=ttl_seconds)


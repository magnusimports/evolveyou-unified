"""
Configurações do Content Service
"""

import os
from functools import lru_cache
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações básicas
    app_name: str = "EvolveYou Content Service"
    version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configurações do servidor
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8080))
    
    # Configurações do Firebase
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "evolveyou-23580")
    firebase_credentials_path: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Configurações de cache
    cache_ttl: int = int(os.getenv("CACHE_TTL", 3600))  # 1 hora
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    
    # Configurações de logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Configurações de paginação
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Configurações de rate limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", 60))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Obter configurações da aplicação (cached)"""
    return Settings()


"""
Configurações do Tracking Service
"""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações do serviço de tracking"""
    
    # Configurações básicas
    app_name: str = "EvolveYou Tracking Service"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Configurações do servidor
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")
    
    # Configurações do Firebase
    firebase_project_id: str = Field(default="evolveyou-23580", env="FIREBASE_PROJECT_ID")
    firebase_credentials_path: Optional[str] = Field(default=None, env="FIREBASE_CREDENTIALS_PATH")
    
    # URLs dos outros microserviços
    users_service_url: str = Field(default="http://localhost:8081", env="USERS_SERVICE_URL")
    content_service_url: str = Field(default="http://localhost:8082", env="CONTENT_SERVICE_URL")
    plans_service_url: str = Field(default="http://localhost:8083", env="PLANS_SERVICE_URL")
    
    # Configurações de cache
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    cache_ttl_seconds: int = Field(default=300, env="CACHE_TTL_SECONDS")  # 5 minutos
    
    # Configurações de logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Configurações de autenticação
    jwt_secret_key: str = Field(default="your-secret-key", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    
    # Configurações específicas do tracking
    tracking_config: Dict[str, Any] = {
        "calorie_calculation": {
            "met_multiplier": 1.0,  # Multiplicador para valores MET
            "duration_factor": 1.0,  # Fator de duração
            "weight_factor": 1.0,   # Fator de peso
            "default_met_value": 3.5  # Valor MET padrão se não encontrado
        },
        "dashboard_config": {
            "cache_duration_minutes": 5,
            "max_retries": 3,
            "timeout_seconds": 10
        },
        "progress_config": {
            "weight_trend_days": 7,     # Dias para calcular tendência de peso
            "strength_trend_days": 30,  # Dias para calcular tendência de força
            "max_data_points": 100      # Máximo de pontos de dados para gráficos
        },
        "validation_config": {
            "max_weight_kg": 300,       # Peso máximo válido
            "min_weight_kg": 30,        # Peso mínimo válido
            "max_reps": 100,            # Repetições máximas válidas
            "max_weight_lifted_kg": 500, # Peso máximo levantado válido
            "max_workout_duration_minutes": 300  # Duração máxima de treino
        }
    }
    
    # Configurações de rate limiting
    rate_limit_config: Dict[str, Any] = {
        "requests_per_minute": 60,
        "burst_size": 10
    }
    
    # Configurações de monitoramento
    monitoring_config: Dict[str, Any] = {
        "health_check_interval_seconds": 30,
        "metrics_collection_enabled": True,
        "performance_tracking_enabled": True
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instância global das configurações
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Obtém instância singleton das configurações"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Recarrega as configurações"""
    global _settings
    _settings = Settings()
    return _settings


"""
Configurações do Users Service
"""

import os
from functools import lru_cache
from pydantic import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações básicas
    app_name: str = "EvolveYou Users Service"
    version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configurações do servidor
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8080"))
    
    # Firebase
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "evolveyou-23580")
    firebase_credentials_path: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    jwt_refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Segurança
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    
    # Rate Limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # segundos
    
    # Cache
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hora
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "json"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://evolveyou.com.br",
        "https://app.evolveyou.com.br",
        "https://admin.evolveyou.com.br"
    ]
    
    # Pub/Sub (para comunicação entre serviços)
    pubsub_topic_onboarding: str = "onboarding-completed"
    pubsub_subscription_plans: str = "plans-service-subscription"
    
    # Serviços externos
    content_service_url: str = os.getenv("CONTENT_SERVICE_URL", "http://localhost:8081")
    plans_service_url: str = os.getenv("PLANS_SERVICE_URL", "http://localhost:8082")
    
    # Upload de arquivos
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Algoritmo calórico
    bmr_formula: str = "mifflin_st_jeor"  # ou "harris_benedict"
    
    # Configurações de onboarding
    onboarding_steps: List[str] = [
        "personal_info",
        "health_assessment", 
        "fitness_goals",
        "lifestyle_assessment",
        "medical_history",
        "body_composition",
        "preferences"
    ]
    
    # Fatores de ajuste do algoritmo calórico
    body_composition_factors: dict = {
        "muito_baixo": 0.85,    # <10% homens, <16% mulheres
        "baixo": 0.90,          # 10-15% homens, 16-20% mulheres  
        "normal": 1.0,          # 15-20% homens, 20-25% mulheres
        "alto": 1.05,           # 20-25% homens, 25-30% mulheres
        "muito_alto": 1.10      # >25% homens, >30% mulheres
    }
    
    pharma_factors: dict = {
        "nenhum": 1.0,
        "termogenico": 1.05,
        "creatina": 1.02,
        "whey_protein": 1.01,
        "multivitaminico": 1.0,
        "omega3": 1.0,
        "cafeina": 1.03,
        "pre_treino": 1.04
    }
    
    training_experience_factors: dict = {
        "iniciante": 0.95,      # 0-6 meses
        "intermediario": 1.0,   # 6 meses - 2 anos
        "avancado": 1.05,       # 2-5 anos
        "expert": 1.10          # >5 anos
    }
    
    activity_factors: dict = {
        "sedentario": 1.2,          # Pouco ou nenhum exercício
        "levemente_ativo": 1.375,   # Exercício leve 1-3 dias/semana
        "moderadamente_ativo": 1.55, # Exercício moderado 3-5 dias/semana
        "muito_ativo": 1.725,       # Exercício pesado 6-7 dias/semana
        "extremamente_ativo": 1.9   # Exercício muito pesado, trabalho físico
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton das configurações"""
    return Settings()


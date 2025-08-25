"""
Configurações do Plans Service
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações básicas
    app_name: str = "EvolveYou Plans Service"
    version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configurações do servidor
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8082"))
    
    # Firebase
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "evolveyou-23580")
    firebase_credentials_path: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
    jwt_algorithm: str = "HS256"
    
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
    
    # Serviços externos
    content_service_url: str = os.getenv("CONTENT_SERVICE_URL", "https://content-service-278319877545.southamerica-east1.run.app")
    users_service_url: str = os.getenv("USERS_SERVICE_URL", "http://localhost:8081")
    
    # Configurações de algoritmos de dieta
    diet_algorithm_config: Dict = {
        # Distribuição de calorias por refeição (%)
        "meal_distribution": {
            "cafe_da_manha": 0.25,      # 25%
            "lanche_manha": 0.10,       # 10%
            "almoco": 0.30,             # 30%
            "lanche_tarde": 0.10,       # 10%
            "jantar": 0.20,             # 20%
            "ceia": 0.05                # 5%
        },
        
        # Distribuição de macronutrientes por refeição
        "macro_distribution": {
            "cafe_da_manha": {"protein": 0.20, "carbs": 0.50, "fat": 0.30},
            "lanche_manha": {"protein": 0.30, "carbs": 0.40, "fat": 0.30},
            "almoco": {"protein": 0.35, "carbs": 0.45, "fat": 0.20},
            "lanche_tarde": {"protein": 0.40, "carbs": 0.35, "fat": 0.25},
            "jantar": {"protein": 0.40, "carbs": 0.35, "fat": 0.25},
            "ceia": {"protein": 0.50, "carbs": 0.20, "fat": 0.30}
        },
        
        # Tolerância para balanceamento (±%)
        "tolerance": {
            "calories": 0.05,           # ±5%
            "protein": 0.10,            # ±10%
            "carbs": 0.15,              # ±15%
            "fat": 0.15                 # ±15%
        },
        
        # Configurações de variação
        "variation": {
            "consistent_days": 3,       # Dias para repetir mesmo plano
            "varied_rotation": 7,       # Dias de rotação para planos variados
            "min_food_variety": 15,     # Mínimo de alimentos diferentes por semana
            "max_repetition": 2         # Máximo de repetições do mesmo alimento por dia
        }
    }
    
    # Configurações de algoritmos de treino
    workout_algorithm_config: Dict = {
        # Splits de treino por dias disponíveis
        "training_splits": {
            1: "full_body",
            2: "upper_lower",
            3: "push_pull_legs",
            4: "upper_lower_push_pull",
            5: "push_pull_legs_upper_lower",
            6: "push_pull_legs_push_pull_legs",
            7: "daily_specialization"
        },
        
        # Volume por nível de experiência
        "volume_config": {
            "beginner": {
                "sets_per_muscle": {"min": 8, "max": 12},
                "exercises_per_muscle": {"min": 2, "max": 3},
                "reps_range": {"strength": [6, 8], "hypertrophy": [8, 12], "endurance": [12, 15]}
            },
            "intermediate": {
                "sets_per_muscle": {"min": 12, "max": 18},
                "exercises_per_muscle": {"min": 3, "max": 4},
                "reps_range": {"strength": [4, 6], "hypertrophy": [6, 12], "endurance": [12, 20]}
            },
            "advanced": {
                "sets_per_muscle": {"min": 16, "max": 24},
                "exercises_per_muscle": {"min": 4, "max": 6},
                "reps_range": {"strength": [3, 5], "hypertrophy": [6, 15], "endurance": [15, 25]}
            },
            "expert": {
                "sets_per_muscle": {"min": 20, "max": 30},
                "exercises_per_muscle": {"min": 5, "max": 8},
                "reps_range": {"strength": [1, 4], "hypertrophy": [6, 20], "endurance": [15, 30]}
            }
        },
        
        # Intensidade por objetivo
        "intensity_config": {
            "perder_peso": {
                "rest_between_sets": {"min": 30, "max": 60},
                "rest_between_exercises": {"min": 60, "max": 90},
                "cardio_percentage": 0.30,
                "strength_percentage": 0.70
            },
            "ganhar_massa": {
                "rest_between_sets": {"min": 60, "max": 120},
                "rest_between_exercises": {"min": 90, "max": 180},
                "cardio_percentage": 0.10,
                "strength_percentage": 0.90
            },
            "aumentar_forca": {
                "rest_between_sets": {"min": 120, "max": 300},
                "rest_between_exercises": {"min": 180, "max": 300},
                "cardio_percentage": 0.05,
                "strength_percentage": 0.95
            },
            "melhorar_resistencia": {
                "rest_between_sets": {"min": 15, "max": 45},
                "rest_between_exercises": {"min": 30, "max": 60},
                "cardio_percentage": 0.50,
                "strength_percentage": 0.50
            },
            "manter_peso": {
                "rest_between_sets": {"min": 45, "max": 90},
                "rest_between_exercises": {"min": 60, "max": 120},
                "cardio_percentage": 0.25,
                "strength_percentage": 0.75
            }
        },
        
        # Aquecimentos por tipo de treino
        "warmup_config": {
            "upper_body": {
                "duration_minutes": 8,
                "exercises": ["arm_circles", "shoulder_rolls", "band_pull_aparts", "light_cardio"]
            },
            "lower_body": {
                "duration_minutes": 10,
                "exercises": ["leg_swings", "hip_circles", "bodyweight_squats", "light_cardio"]
            },
            "full_body": {
                "duration_minutes": 12,
                "exercises": ["jumping_jacks", "arm_circles", "leg_swings", "dynamic_stretching"]
            },
            "cardio": {
                "duration_minutes": 5,
                "exercises": ["light_walking", "joint_mobility", "dynamic_stretching"]
            }
        }
    }
    
    # Configurações de templates de apresentação
    presentation_config: Dict = {
        # Templates por objetivo
        "templates": {
            "perder_peso": {
                "motivational_phrases": [
                    "Cada escolha saudável te aproxima do seu objetivo! 💪",
                    "Você está no caminho certo para transformar seu corpo! 🔥",
                    "Consistência é a chave para o sucesso! Continue assim! ⭐"
                ],
                "focus_areas": ["deficit_calorico", "cardio", "hidratacao"],
                "tips": [
                    "Beba água antes das refeições para aumentar a saciedade",
                    "Priorize proteínas para manter a massa muscular",
                    "Inclua exercícios de força para acelerar o metabolismo"
                ]
            },
            "ganhar_massa": {
                "motivational_phrases": [
                    "Construa o corpo dos seus sonhos, um treino de cada vez! 🏗️",
                    "Músculos são construídos na academia e na cozinha! 🍽️",
                    "Seja paciente, o crescimento muscular é um processo! 📈"
                ],
                "focus_areas": ["superavit_calorico", "proteina", "descanso"],
                "tips": [
                    "Consuma proteína a cada 3-4 horas",
                    "Priorize exercícios compostos para máximo ganho",
                    "Durma 7-9 horas para otimizar a recuperação"
                ]
            },
            "aumentar_forca": {
                "motivational_phrases": [
                    "Força não é só física, é mental! Supere seus limites! 💥",
                    "Cada repetição te torna mais forte que ontem! ⚡",
                    "A força verdadeira vem da consistência! 🔨"
                ],
                "focus_areas": ["progressao_carga", "tecnica", "recuperacao"],
                "tips": [
                    "Foque na técnica perfeita antes de aumentar a carga",
                    "Descanse adequadamente entre as séries",
                    "Registre seus progressos para acompanhar a evolução"
                ]
            },
            "melhorar_resistencia": {
                "motivational_phrases": [
                    "Resistência é sobre não desistir quando fica difícil! 🏃",
                    "Cada batimento do coração te torna mais resistente! ❤️",
                    "Sua capacidade é maior do que você imagina! 🌟"
                ],
                "focus_areas": ["cardio", "hidratacao", "recuperacao_ativa"],
                "tips": [
                    "Aumente gradualmente a intensidade dos exercícios",
                    "Mantenha-se hidratado durante os treinos",
                    "Inclua recuperação ativa nos dias de descanso"
                ]
            },
            "manter_peso": {
                "motivational_phrases": [
                    "Manter é tão desafiador quanto conquistar! Parabéns! 🎯",
                    "Você encontrou o equilíbrio perfeito! Continue assim! ⚖️",
                    "Consistência é sua maior aliada na manutenção! 🔄"
                ],
                "focus_areas": ["equilibrio", "variedade", "sustentabilidade"],
                "tips": [
                    "Varie seus treinos para manter a motivação",
                    "Mantenha flexibilidade na dieta sem exageros",
                    "Monitore seu peso semanalmente, não diariamente"
                ]
            }
        },
        
        # Configurações de personalização
        "personalization": {
            "use_user_name": True,
            "include_progress_tracking": True,
            "show_weekly_summary": True,
            "motivational_frequency": "daily"
        }
    }
    
    # Configurações de cache e performance
    cache_config: Dict = {
        "diet_plans_ttl": 86400,        # 24 horas
        "workout_plans_ttl": 604800,    # 7 dias
        "user_preferences_ttl": 3600,   # 1 hora
        "content_data_ttl": 7200,       # 2 horas
        "presentation_ttl": 1800        # 30 minutos
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton das configurações"""
    return Settings()


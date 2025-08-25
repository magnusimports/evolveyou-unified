"""
Configuração global dos testes
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
import os
import sys
from datetime import datetime, date

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configurar variáveis de ambiente para testes
os.environ.update({
    "ENVIRONMENT": "test",
    "JWT_SECRET_KEY": "test_secret_key_for_testing_only",
    "JWT_ALGORITHM": "HS256",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "7",
    "FIREBASE_PROJECT_ID": "test-project",
    "LOG_LEVEL": "INFO",
    "RATE_LIMIT_REQUESTS": "100",
    "RATE_LIMIT_WINDOW": "60"
})

@pytest.fixture(scope="session")
def event_loop():
    """Criar event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_firebase_app():
    """Mock da aplicação Firebase"""
    mock_app = Mock()
    mock_app.project_id = "test-project"
    return mock_app

@pytest.fixture
def mock_firestore_client():
    """Mock do cliente Firestore"""
    mock_client = Mock()
    
    # Mock das coleções
    mock_collection = Mock()
    mock_document = Mock()
    mock_document.id = "test_doc_id"
    mock_document.set = Mock()
    mock_document.get = Mock()
    mock_document.update = Mock()
    
    mock_collection.document.return_value = mock_document
    mock_collection.where.return_value = mock_collection
    mock_collection.limit.return_value = mock_collection
    mock_collection.get.return_value = []
    
    mock_client.collection.return_value = mock_collection
    
    return mock_client

@pytest.fixture
def sample_user_data():
    """Dados de usuário de exemplo para testes"""
    return {
        "id": "test_user_123",
        "email": "test@evolveyou.com.br",
        "name": "João Silva",
        "date_of_birth": "1990-05-15",
        "gender": "male",
        "is_active": True,
        "is_verified": False,
        "is_premium": False,
        "onboarding_completed": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "terms_accepted": True,
        "privacy_accepted": True,
        "marketing_consent": False
    }

@pytest.fixture
def sample_onboarding_data():
    """Dados de onboarding de exemplo"""
    return {
        "health_assessment": {
            "height": 175.0,
            "weight": 80.0,
            "body_fat_percentage": 15.0,
            "waist_circumference": 85.0,
            "hip_circumference": 95.0,
            "resting_heart_rate": 65,
            "max_heart_rate": 185,
            "systolic_pressure": 120,
            "diastolic_pressure": 80
        },
        "medical_history": {
            "chronic_conditions": [],
            "medications": [],
            "supplements": ["creatina", "whey protein"],
            "allergies": [],
            "injuries": [],
            "surgeries": []
        },
        "lifestyle_assessment": {
            "work_activity_level": "sedentary",
            "leisure_activity_level": "moderately_active",
            "available_days_per_week": 4,
            "preferred_workout_duration": 60,
            "sleep_hours": 7.5,
            "stress_level": 3,
            "water_intake": 2.5,
            "alcohol_consumption": "occasional",
            "smoking_status": "never"
        },
        "fitness_goals": {
            "primary_goal": "ganhar_massa",
            "target_weight": 85.0,
            "timeline_weeks": 16,
            "training_experience": "intermediate",
            "available_days_per_week": 4,
            "preferred_workout_types": ["musculacao", "cardio"],
            "specific_goals": ["aumentar_massa_muscular", "melhorar_forca"]
        },
        "preferences": {
            "units": "metric",
            "language": "pt_BR",
            "timezone": "America/Sao_Paulo",
            "notifications": {
                "workout_reminders": True,
                "meal_reminders": True,
                "progress_check_ins": True,
                "motivational_messages": True
            },
            "privacy": {
                "profile_visibility": "private",
                "share_progress": False,
                "data_analytics": True
            }
        }
    }

@pytest.fixture
def sample_calorie_calculation():
    """Cálculo calórico de exemplo"""
    return {
        "bmr": 1750.5,
        "tdee": 2275.7,
        "body_composition_factor": 1.05,
        "pharma_factor": 1.02,
        "training_experience_factor": 1.0,
        "activity_factor": 1.3,
        "maintenance_calories": 2275.7,
        "cutting_calories": 1820.6,
        "bulking_calories": 2617.1,
        "protein_grams": 160.0,
        "carbs_grams": 256.0,
        "fat_grams": 76.0,
        "calculated_at": datetime.utcnow().isoformat(),
        "formula_used": "mifflin_st_jeor"
    }

@pytest.fixture
def mock_settings():
    """Mock das configurações"""
    from src.config.settings import Settings
    
    settings = Settings()
    settings.environment = "test"
    settings.jwt_secret_key = "test_secret_key"
    settings.firebase_project_id = "test-project"
    settings.debug = True
    
    # Fatores para cálculos
    settings.body_composition_factors = {
        "muito_baixo": 1.1,
        "baixo": 1.05,
        "normal": 1.0,
        "alto": 0.95,
        "muito_alto": 0.9
    }
    
    settings.pharma_factors = {
        "termogenico": 1.05,
        "creatina": 1.02,
        "whey_protein": 1.01,
        "multivitaminico": 1.01,
        "omega3": 1.01,
        "cafeina": 1.03,
        "pre_treino": 1.04
    }
    
    settings.training_experience_factors = {
        "beginner": 0.95,
        "intermediate": 1.0,
        "advanced": 1.05,
        "expert": 1.1
    }
    
    settings.activity_factors = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extremely_active": 1.9
    }
    
    return settings

@pytest.fixture
def mock_jwt_payload():
    """Payload JWT de exemplo"""
    return {
        "sub": "test_user_123",
        "type": "access",
        "iat": datetime.utcnow().timestamp(),
        "exp": (datetime.utcnow().timestamp() + 1800),  # 30 minutos
        "iss": "evolveyou-users-service"
    }

@pytest.fixture
def mock_http_client():
    """Mock do cliente HTTP"""
    mock_client = AsyncMock()
    
    # Mock de resposta HTTP
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_response.text = "OK"
    
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    mock_client.put.return_value = mock_response
    mock_client.delete.return_value = mock_response
    
    return mock_client

@pytest.fixture
def mock_logger():
    """Mock do logger estruturado"""
    mock_logger = Mock()
    mock_logger.info = Mock()
    mock_logger.warning = Mock()
    mock_logger.error = Mock()
    mock_logger.debug = Mock()
    mock_logger.bind.return_value = mock_logger
    return mock_logger

# Fixtures para testes de integração
@pytest.fixture
def integration_test_user():
    """Usuário para testes de integração"""
    return {
        "email": f"integration_test_{datetime.utcnow().timestamp()}@test.com",
        "password": "TestPassword123!",
        "name": "Integration Test User",
        "date_of_birth": date(1990, 1, 1),
        "gender": "male"
    }

# Configurações de pytest
def pytest_configure(config):
    """Configuração do pytest"""
    # Adicionar marcadores customizados
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes lentos"
    )
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )

def pytest_collection_modifyitems(config, items):
    """Modificar itens da coleção de testes"""
    # Adicionar marcador 'unit' para testes que não têm marcadores
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)

# Fixtures de cleanup
@pytest.fixture(autouse=True)
def cleanup_environment():
    """Limpar ambiente após cada teste"""
    yield
    # Cleanup code aqui se necessário
    pass

# Mock para Firebase Admin
@pytest.fixture
def mock_firebase_admin():
    """Mock do Firebase Admin SDK"""
    with pytest.MonkeyPatch.context() as m:
        mock_admin = Mock()
        mock_admin.initialize_app.return_value = Mock()
        mock_admin.get_app.return_value = Mock()
        mock_admin._apps = {}
        
        m.setattr("firebase_admin", mock_admin)
        yield mock_admin

# Fixture para testes que precisam de dados reais
@pytest.fixture
def real_data_test():
    """Indicador para testes que usam dados reais"""
    return os.getenv("USE_REAL_DATA", "false").lower() == "true"


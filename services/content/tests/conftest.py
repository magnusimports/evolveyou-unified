"""
Configuração global para testes do Content Service
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, AsyncMock

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session")
def event_loop():
    """Criar event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_firebase_app():
    """Mock do Firebase App"""
    app = Mock()
    app.project_id = "test-project"
    return app

@pytest.fixture
def mock_firestore_client():
    """Mock do cliente Firestore"""
    client = AsyncMock()
    
    # Mock das operações básicas
    client.collection.return_value.document.return_value.get = AsyncMock()
    client.collection.return_value.document.return_value.set = AsyncMock()
    client.collection.return_value.document.return_value.update = AsyncMock()
    client.collection.return_value.document.return_value.delete = AsyncMock()
    
    # Mock das queries
    client.collection.return_value.where.return_value = client.collection.return_value
    client.collection.return_value.order_by.return_value = client.collection.return_value
    client.collection.return_value.limit.return_value = client.collection.return_value
    client.collection.return_value.offset.return_value = client.collection.return_value
    client.collection.return_value.stream.return_value = AsyncMock()
    
    # Mock do batch
    client.batch.return_value.set = Mock()
    client.batch.return_value.commit = AsyncMock()
    
    return client

@pytest.fixture
def sample_food_data():
    """Dados de exemplo para alimentos"""
    return {
        "id": "food_1",
        "name": "Frango Grelhado",
        "category": "carnes",
        "nutritional_info": {
            "calories": 165,
            "protein": 31,
            "carbs": 0,
            "fat": 3.6,
            "fiber": 0,
            "sugar": 0,
            "sodium": 74
        },
        "serving_sizes": [
            {
                "name": "100g",
                "weight_grams": 100,
                "calories": 165,
                "protein": 31,
                "carbs": 0,
                "fat": 3.6
            },
            {
                "name": "1 peito médio",
                "weight_grams": 150,
                "calories": 248,
                "protein": 46.5,
                "carbs": 0,
                "fat": 5.4
            }
        ],
        "tags": ["proteina", "magro", "ave"],
        "verified": True,
        "source": "TACO"
    }

@pytest.fixture
def sample_exercise_data():
    """Dados de exemplo para exercícios"""
    return {
        "id": "exercise_1",
        "name": "Supino Reto",
        "primary_muscle_group": "peito",
        "secondary_muscle_groups": ["triceps", "ombros"],
        "exercise_type": "forca",
        "equipment": ["barra", "banco"],
        "difficulty": "intermediario",
        "description": "Exercício fundamental para desenvolvimento do peitoral",
        "instructions": [
            "Deite no banco com os pés apoiados no chão",
            "Segure a barra com pegada pronada",
            "Desça a barra até o peito",
            "Empurre a barra para cima até extensão completa"
        ],
        "premium_guidance": {
            "form_tips": [
                "Mantenha os ombros retraídos",
                "Controle a descida da barra"
            ],
            "common_mistakes": [
                "Arquear demais as costas",
                "Não tocar o peito com a barra"
            ],
            "breathing_pattern": "Inspire na descida, expire na subida"
        },
        "met_value": 6.0,
        "tags": ["peito", "forca", "basico"],
        "verified": True
    }

@pytest.fixture
def sample_met_values():
    """Dados de exemplo para valores MET"""
    return [
        {
            "activity": "Musculação - intensidade moderada",
            "met_value": 3.5,
            "exercise_type": "forca",
            "intensity": "moderada"
        },
        {
            "activity": "Corrida - 8 km/h",
            "met_value": 8.3,
            "exercise_type": "cardio",
            "intensity": "moderada"
        },
        {
            "activity": "Yoga - Hatha",
            "met_value": 2.5,
            "exercise_type": "flexibilidade",
            "intensity": "leve"
        }
    ]

# Configurações de ambiente para testes
@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Configurar variáveis de ambiente para testes"""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "test-project")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

# Markers personalizados
def pytest_configure(config):
    """Configurar markers personalizados"""
    config.addinivalue_line(
        "markers", "integration: marca testes de integração que requerem Firebase"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes que demoram para executar"
    )
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )


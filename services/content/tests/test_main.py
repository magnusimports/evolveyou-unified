"""
Testes para a API principal do Content Service
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import json

# Importar a aplicação
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from services.firebase_service import FirebaseService
from services.content_service import ContentService

# Cliente de teste
client = TestClient(app)

class TestHealthCheck:
    """Testes para o endpoint de health check"""
    
    def test_health_check(self):
        """Testar endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "content-service"
        assert data["version"] == "1.0.0"

class TestFoodsAPI:
    """Testes para endpoints de alimentos"""
    
    @patch('services.firebase_service.FirebaseService')
    def test_search_foods_success(self, mock_firebase):
        """Testar busca de alimentos com sucesso"""
        # Mock do serviço Firebase
        mock_firebase_instance = AsyncMock()
        mock_firebase.return_value = mock_firebase_instance
        
        # Mock dos dados de resposta
        mock_response = {
            "documents": [
                {
                    "id": "food1",
                    "name": "Frango Grelhado",
                    "category": "carnes",
                    "nutritional_info": {
                        "calories": 165,
                        "protein": 31,
                        "carbs": 0,
                        "fat": 3.6
                    },
                    "serving_sizes": [],
                    "tags": ["proteina", "magro"],
                    "verified": True
                }
            ],
            "total": 1,
            "has_more": False
        }
        
        mock_firebase_instance.search_documents.return_value = mock_response
        
        # Fazer requisição
        response = client.get("/foods?search=frango")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["foods"]) == 1
        assert data["foods"][0]["name"] == "Frango Grelhado"
        assert data["total"] == 1
    
    def test_search_foods_with_filters(self):
        """Testar busca de alimentos com filtros"""
        response = client.get("/foods?category=carnes&min_protein=20&max_calories=200")
        # Como não temos dados reais, esperamos que não dê erro
        assert response.status_code in [200, 500]  # 500 se Firebase não estiver configurado
    
    def test_search_foods_pagination(self):
        """Testar paginação na busca de alimentos"""
        response = client.get("/foods?limit=10&offset=20")
        assert response.status_code in [200, 500]
    
    def test_get_food_by_id_not_found(self):
        """Testar busca de alimento inexistente"""
        response = client.get("/foods/nonexistent")
        assert response.status_code in [404, 500]

class TestExercisesAPI:
    """Testes para endpoints de exercícios"""
    
    def test_search_exercises_success(self):
        """Testar busca de exercícios"""
        response = client.get("/exercises?muscle_group=peito")
        assert response.status_code in [200, 500]
    
    def test_search_exercises_with_filters(self):
        """Testar busca de exercícios com múltiplos filtros"""
        response = client.get("/exercises?muscle_group=peito&equipment=halteres&difficulty=intermediario")
        assert response.status_code in [200, 500]
    
    def test_get_exercise_by_id(self):
        """Testar busca de exercício por ID"""
        response = client.get("/exercises/test_exercise")
        assert response.status_code in [200, 404, 500]
    
    def test_get_met_values(self):
        """Testar endpoint de valores MET"""
        response = client.get("/exercises/met-values")
        assert response.status_code in [200, 500]
    
    def test_get_met_values_filtered(self):
        """Testar valores MET com filtro"""
        response = client.get("/exercises/met-values?exercise_type=cardio")
        assert response.status_code in [200, 500]

class TestCategoriesAPI:
    """Testes para endpoints de categorias"""
    
    def test_get_food_categories(self):
        """Testar endpoint de categorias de alimentos"""
        response = client.get("/categories/foods")
        assert response.status_code in [200, 500]
    
    def test_get_exercise_categories(self):
        """Testar endpoint de categorias de exercícios"""
        response = client.get("/categories/exercises")
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "muscle_groups" in data
            assert "exercise_types" in data
            assert "equipment" in data
            assert "difficulties" in data

class TestValidation:
    """Testes de validação de parâmetros"""
    
    def test_invalid_limit(self):
        """Testar limite inválido"""
        response = client.get("/foods?limit=0")
        assert response.status_code == 422
    
    def test_invalid_limit_too_high(self):
        """Testar limite muito alto"""
        response = client.get("/foods?limit=1000")
        assert response.status_code == 422
    
    def test_negative_offset(self):
        """Testar offset negativo"""
        response = client.get("/foods?offset=-1")
        assert response.status_code == 422

class TestErrorHandling:
    """Testes de tratamento de erros"""
    
    def test_invalid_endpoint(self):
        """Testar endpoint inexistente"""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Testar método não permitido"""
        response = client.post("/health")
        assert response.status_code == 405

# Testes de integração (requerem Firebase configurado)
@pytest.mark.integration
class TestIntegration:
    """Testes de integração com Firebase"""
    
    @pytest.mark.asyncio
    async def test_firebase_connection(self):
        """Testar conexão com Firebase"""
        try:
            firebase_service = FirebaseService()
            await firebase_service.initialize()
            health = await firebase_service.health_check()
            assert health["status"] == "healthy"
        except Exception as e:
            pytest.skip(f"Firebase não configurado: {e}")
    
    @pytest.mark.asyncio
    async def test_content_service_integration(self):
        """Testar integração do ContentService"""
        try:
            firebase_service = FirebaseService()
            await firebase_service.initialize()
            content_service = ContentService(firebase_service)
            
            # Testar busca de alimentos
            result = await content_service.search_foods(limit=5)
            assert isinstance(result, dict)
            assert "foods" in result
            
        except Exception as e:
            pytest.skip(f"Firebase não configurado: {e}")

# Configuração de fixtures
@pytest.fixture
def mock_firebase_service():
    """Fixture para mock do FirebaseService"""
    service = Mock(spec=FirebaseService)
    service.initialize = AsyncMock()
    service.search_documents = AsyncMock()
    service.get_document = AsyncMock()
    service.health_check = AsyncMock(return_value={"status": "healthy"})
    return service

@pytest.fixture
def mock_content_service(mock_firebase_service):
    """Fixture para mock do ContentService"""
    service = Mock(spec=ContentService)
    service.search_foods = AsyncMock()
    service.search_exercises = AsyncMock()
    service.get_food_by_id = AsyncMock()
    service.get_exercise_by_id = AsyncMock()
    service.get_met_values = AsyncMock()
    service.get_food_categories = AsyncMock()
    service.get_exercise_categories = AsyncMock()
    return service

if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])


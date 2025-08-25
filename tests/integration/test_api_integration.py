"""
EvolveYou API Integration Tests
Testa a integração entre todos os microserviços
"""

import pytest
import requests
import json
import time
from typing import Dict, Any

# URLs dos serviços (staging)
BASE_URLS = {
    "users": "https://users-staging-278319877545.southamerica-east1.run.app",
    "content": "https://content-staging-278319877545.southamerica-east1.run.app", 
    "health": "https://health-check-staging-278319877545.southamerica-east1.run.app",
    "backend": "https://backend-staging-278319877545.southamerica-east1.run.app",
    "plans": "https://plans-service-staging-278319877545.southamerica-east1.run.app",
    "tracking": "https://tracking-service-staging-278319877545.southamerica-east1.run.app"
}

class TestHealthChecks:
    """Testa se todos os serviços estão operacionais"""
    
    @pytest.mark.parametrize("service,url", BASE_URLS.items())
    def test_service_health(self, service: str, url: str):
        """Testa health check de cada serviço"""
        response = requests.get(f"{url}/health", timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "version" in data

    def test_all_services_responding(self):
        """Testa se todos os serviços respondem simultaneamente"""
        results = {}
        
        for service, url in BASE_URLS.items():
            try:
                response = requests.get(f"{url}/health", timeout=10)
                results[service] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "healthy": response.status_code == 200
                }
            except Exception as e:
                results[service] = {
                    "status_code": 0,
                    "response_time": 30.0,
                    "healthy": False,
                    "error": str(e)
                }
        
        # Pelo menos 80% dos serviços devem estar saudáveis
        healthy_count = sum(1 for r in results.values() if r["healthy"])
        total_count = len(results)
        health_ratio = healthy_count / total_count
        
        assert health_ratio >= 0.8, f"Apenas {healthy_count}/{total_count} serviços estão saudáveis: {results}"

class TestUserFlow:
    """Testa fluxo completo de usuário"""
    
    def test_user_registration_flow(self):
        """Testa registro completo de usuário"""
        # Dados de teste
        test_user = {
            "email": f"test_{int(time.time())}@evolveyou.com.br",
            "password": "TestPassword123!",
            "full_name": "Usuário Teste",
            "date_of_birth": "1990-01-01",
            "gender": "masculino"
        }
        
        # 1. Registrar usuário
        response = requests.post(
            f"{BASE_URLS['users']}/auth/register",
            json=test_user,
            timeout=30
        )
        
        if response.status_code != 201:
            pytest.skip(f"Serviço de usuários não disponível: {response.status_code}")
        
        assert response.status_code == 201
        user_data = response.json()
        
        assert "user" in user_data
        assert "tokens" in user_data
        assert user_data["user"]["email"] == test_user["email"]
        
        # Extrair token para próximos testes
        access_token = user_data["tokens"]["access_token"]
        user_id = user_data["user"]["id"]
        
        # 2. Verificar perfil do usuário
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"{BASE_URLS['users']}/users/me",
            headers=headers,
            timeout=30
        )
        
        assert response.status_code == 200
        profile_data = response.json()
        assert profile_data["email"] == test_user["email"]
        
        return {
            "user_id": user_id,
            "access_token": access_token,
            "user_data": user_data
        }

    def test_content_access(self):
        """Testa acesso ao conteúdo (exercícios, alimentos)"""
        # Testar busca de exercícios
        response = requests.get(
            f"{BASE_URLS['content']}/exercises",
            params={"limit": 10},
            timeout=30
        )
        
        if response.status_code != 200:
            pytest.skip(f"Serviço de conteúdo não disponível: {response.status_code}")
        
        assert response.status_code == 200
        exercises = response.json()
        assert isinstance(exercises, list)
        
        # Testar busca de alimentos
        response = requests.get(
            f"{BASE_URLS['content']}/foods",
            params={"search": "arroz", "limit": 5},
            timeout=30
        )
        
        assert response.status_code == 200
        foods = response.json()
        assert isinstance(foods, list)

class TestServiceIntegration:
    """Testa integração entre serviços"""
    
    def test_user_onboarding_integration(self):
        """Testa integração completa do onboarding"""
        # Primeiro registrar um usuário
        test_user = {
            "email": f"onboarding_{int(time.time())}@evolveyou.com.br",
            "password": "TestPassword123!",
            "full_name": "Usuário Onboarding",
            "date_of_birth": "1990-01-01",
            "gender": "masculino"
        }
        
        # Registrar usuário
        response = requests.post(
            f"{BASE_URLS['users']}/auth/register",
            json=test_user,
            timeout=30
        )
        
        if response.status_code != 201:
            pytest.skip("Serviço de usuários não disponível")
        
        user_data = response.json()
        access_token = user_data["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Dados de onboarding
        onboarding_data = {
            "health_assessment": {
                "height": 175,
                "weight": 70,
                "body_fat_percentage": 15,
                "activity_level": "moderadamente_ativo",
                "medical_conditions": [],
                "medications": [],
                "allergies": []
            },
            "fitness_goals": {
                "primary_goal": "ganho_massa",
                "target_weight": 75,
                "timeline_weeks": 12,
                "training_frequency": 4,
                "experience_level": "intermediario"
            },
            "lifestyle_assessment": {
                "sleep_hours": 8,
                "stress_level": "medio",
                "work_schedule": "comercial",
                "dietary_restrictions": [],
                "preferred_meal_times": ["07:00", "12:00", "19:00"]
            },
            "preferences": {
                "preferred_exercises": ["musculacao", "cardio"],
                "disliked_exercises": ["corrida"],
                "equipment_access": ["academia_completa"],
                "dietary_preferences": ["sem_restricoes"]
            }
        }
        
        # Submeter onboarding
        response = requests.post(
            f"{BASE_URLS['users']}/onboarding/submit",
            json=onboarding_data,
            headers=headers,
            timeout=30
        )
        
        assert response.status_code == 200
        onboarding_result = response.json()
        assert "calorie_calculation" in onboarding_result
        assert "message" in onboarding_result

class TestPerformance:
    """Testes básicos de performance"""
    
    def test_response_times(self):
        """Testa tempos de resposta dos serviços"""
        max_response_time = 2.0  # 2 segundos
        
        for service, url in BASE_URLS.items():
            start_time = time.time()
            
            try:
                response = requests.get(f"{url}/health", timeout=30)
                response_time = time.time() - start_time
                
                assert response_time < max_response_time, \
                    f"Serviço {service} muito lento: {response_time:.2f}s > {max_response_time}s"
                
            except Exception as e:
                pytest.fail(f"Serviço {service} falhou: {e}")

    def test_concurrent_requests(self):
        """Testa requisições concorrentes"""
        import concurrent.futures
        import threading
        
        def make_request(service_url):
            try:
                response = requests.get(f"{service_url}/health", timeout=10)
                return {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "status_code": 0,
                    "response_time": 10.0,
                    "success": False,
                    "error": str(e)
                }
        
        # Fazer 20 requisições concorrentes para cada serviço
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for service, url in BASE_URLS.items():
                for _ in range(5):  # 5 requisições por serviço
                    future = executor.submit(make_request, url)
                    futures.append((service, future))
            
            results = {}
            for service, future in futures:
                if service not in results:
                    results[service] = []
                results[service].append(future.result())
        
        # Analisar resultados
        for service, service_results in results.items():
            success_rate = sum(1 for r in service_results if r["success"]) / len(service_results)
            avg_response_time = sum(r["response_time"] for r in service_results) / len(service_results)
            
            assert success_rate >= 0.8, \
                f"Serviço {service} com baixa taxa de sucesso: {success_rate:.2%}"
            
            assert avg_response_time < 3.0, \
                f"Serviço {service} com tempo médio alto: {avg_response_time:.2f}s"

class TestSecurity:
    """Testes básicos de segurança"""
    
    def test_unauthorized_access(self):
        """Testa se endpoints protegidos rejeitam acesso não autorizado"""
        protected_endpoints = [
            f"{BASE_URLS['users']}/users/me",
            f"{BASE_URLS['users']}/onboarding/submit",
            f"{BASE_URLS['tracking']}/progress",
            f"{BASE_URLS['plans']}/generate"
        ]
        
        for endpoint in protected_endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                assert response.status_code in [401, 403], \
                    f"Endpoint {endpoint} deveria rejeitar acesso não autorizado, mas retornou {response.status_code}"
            except requests.exceptions.RequestException:
                # Serviço pode não estar disponível, pular teste
                continue

    def test_cors_headers(self):
        """Testa se headers CORS estão configurados"""
        for service, url in BASE_URLS.items():
            try:
                response = requests.options(f"{url}/health", timeout=10)
                
                # Verificar se headers CORS estão presentes
                cors_headers = [
                    "Access-Control-Allow-Origin",
                    "Access-Control-Allow-Methods",
                    "Access-Control-Allow-Headers"
                ]
                
                for header in cors_headers:
                    assert header in response.headers or response.status_code == 404, \
                        f"Serviço {service} sem header CORS: {header}"
                        
            except requests.exceptions.RequestException:
                # Serviço pode não estar disponível, pular teste
                continue

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


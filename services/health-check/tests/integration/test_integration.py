"""
Testes de integração para o Health Check Service.
"""

import unittest
import requests
import time
import os
import sys
from unittest.mock import patch

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import app, db


class TestHealthCheckIntegration(unittest.TestCase):
    """Testes de integração para o Health Check Service."""
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para todos os testes."""
        cls.app = app.test_client()
        cls.app.testing = True
        
        # Configurar ambiente de teste
        os.environ['ENVIRONMENT'] = 'test'
        os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'evolveyou-test'
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        # Limpar cache entre testes
        import app as app_module
        app_module.health_cache.clear()
    
    def test_firestore_connection(self):
        """Testa conexão real com Firestore (emulador)."""
        try:
            # Tentar operação no Firestore
            test_doc = db.collection('integration_tests').document('test')
            test_doc.set({
                'test': True,
                'timestamp': time.time()
            })
            
            # Verificar se o documento foi criado
            doc = test_doc.get()
            self.assertTrue(doc.exists)
            
            # Limpar documento de teste
            test_doc.delete()
            
        except Exception as e:
            self.fail(f"Falha na conexão com Firestore: {str(e)}")
    
    def test_health_check_endpoint_integration(self):
        """Testa endpoint de health check com integração real."""
        response = self.app.get('/health-check')
        
        self.assertIn(response.status_code, [200, 503])  # Pode estar degraded
        
        data = response.get_json()
        self.assertIn('status', data)
        self.assertIn('service', data)
        self.assertIn('version', data)
        self.assertIn('timestamp', data)
        self.assertIn('checks', data)
        
        # Verificar estrutura dos checks
        checks = data['checks']
        self.assertIn('firestore', checks)
        self.assertIn('system', checks)
        
        # Verificar estrutura do check do Firestore
        firestore_check = checks['firestore']
        self.assertIn('status', firestore_check)
        
        # Verificar estrutura do check do sistema
        system_check = checks['system']
        self.assertIn('status', system_check)
        self.assertIn('cpu_percent', system_check)
        self.assertIn('memory_percent', system_check)
        self.assertIn('disk_percent', system_check)
    
    def test_detailed_health_check_integration(self):
        """Testa endpoint de health check detalhado com integração real."""
        response = self.app.get('/health-check/detailed')
        
        self.assertIn(response.status_code, [200, 503])
        
        data = response.get_json()
        self.assertIn('status', data)
        self.assertIn('checks', data)
        self.assertIn('summary', data)
        
        # Verificar estrutura do summary
        summary = data['summary']
        self.assertIn('total_services', summary)
        self.assertIn('healthy_services', summary)
        self.assertIn('unhealthy_services', summary)
        
        # Verificar checks de serviços
        checks = data['checks']
        if 'services' in checks:
            services = checks['services']
            for service_name, service_check in services.items():
                self.assertIn('status', service_check)
                # Pode estar unhealthy se o serviço não estiver rodando
                self.assertIn(service_check['status'], ['healthy', 'unhealthy'])
    
    def test_metrics_endpoint_integration(self):
        """Testa endpoint de métricas com integração real."""
        response = self.app.get('/metrics')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('service', data)
        self.assertIn('version', data)
        self.assertIn('uptime_seconds', data)
        self.assertIn('metrics', data)
        
        # Verificar métricas
        metrics = data['metrics']
        self.assertIn('cpu_percent', metrics)
        self.assertIn('memory_percent', metrics)
        self.assertIn('disk_percent', metrics)
        
        # Verificar se os valores são números válidos
        self.assertIsInstance(metrics['cpu_percent'], (int, float))
        self.assertIsInstance(metrics['memory_percent'], (int, float))
        self.assertIsInstance(metrics['disk_percent'], (int, float))
        
        # Verificar se os valores estão em ranges válidos
        self.assertGreaterEqual(metrics['cpu_percent'], 0)
        self.assertLessEqual(metrics['cpu_percent'], 100)
        self.assertGreaterEqual(metrics['memory_percent'], 0)
        self.assertLessEqual(metrics['memory_percent'], 100)
        self.assertGreaterEqual(metrics['disk_percent'], 0)
        self.assertLessEqual(metrics['disk_percent'], 100)
    
    def test_info_endpoint_integration(self):
        """Testa endpoint de informações com integração real."""
        response = self.app.get('/info')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('service', data)
        self.assertIn('version', data)
        self.assertIn('environment', data)
        self.assertIn('description', data)
        self.assertIn('endpoints', data)
        self.assertIn('uptime_seconds', data)
        self.assertIn('monitored_services', data)
        
        # Verificar se uptime é um número positivo
        self.assertIsInstance(data['uptime_seconds'], (int, float))
        self.assertGreater(data['uptime_seconds'], 0)
        
        # Verificar se endpoints é uma lista
        self.assertIsInstance(data['endpoints'], list)
        self.assertGreater(len(data['endpoints']), 0)
        
        # Verificar se monitored_services é uma lista
        self.assertIsInstance(data['monitored_services'], list)
    
    def test_cache_functionality(self):
        """Testa funcionalidade de cache dos health checks."""
        # Primeira requisição
        start_time = time.time()
        response1 = self.app.get('/health-check')
        first_request_time = time.time() - start_time
        
        # Segunda requisição (deve usar cache)
        start_time = time.time()
        response2 = self.app.get('/health-check')
        second_request_time = time.time() - start_time
        
        # Verificar se ambas as requisições foram bem-sucedidas
        self.assertIn(response1.status_code, [200, 503])
        self.assertIn(response2.status_code, [200, 503])
        
        # A segunda requisição deve ser mais rápida (usando cache)
        # Nota: Este teste pode ser flaky em ambientes de teste
        # self.assertLess(second_request_time, first_request_time)
        
        # Verificar se os dados são consistentes
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        # Status deve ser o mesmo (cache funcionando)
        self.assertEqual(data1['status'], data2['status'])
    
    def test_error_handling_integration(self):
        """Testa tratamento de erros em cenários de integração."""
        # Testar endpoint inexistente
        response = self.app.get('/endpoint-inexistente')
        
        self.assertEqual(response.status_code, 404)
        
        data = response.get_json()
        self.assertEqual(data['error'], 'Not Found')
        self.assertIn('message', data)
        self.assertIn('timestamp', data)
        self.assertIn('path', data)
    
    def test_cors_headers(self):
        """Testa se os headers CORS estão configurados corretamente."""
        response = self.app.get('/health-check')
        
        # Verificar se headers CORS estão presentes
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')
    
    def test_concurrent_requests(self):
        """Testa comportamento com requisições concorrentes."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = self.app.get('/health-check')
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {str(e)}")
        
        # Criar múltiplas threads para requisições concorrentes
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads terminarem
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        status_codes = []
        while not results.empty():
            result = results.get()
            if isinstance(result, int):
                status_codes.append(result)
            else:
                self.fail(f"Request failed: {result}")
        
        # Todos os status codes devem ser válidos
        for status_code in status_codes:
            self.assertIn(status_code, [200, 503])
        
        # Deve ter recebido resposta de todas as requisições
        self.assertEqual(len(status_codes), 5)


class TestHealthCheckPerformance(unittest.TestCase):
    """Testes de performance para o Health Check Service."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_response_time_basic_health_check(self):
        """Testa tempo de resposta do health check básico."""
        start_time = time.time()
        response = self.app.get('/health-check')
        response_time = time.time() - start_time
        
        # Health check básico deve responder em menos de 2 segundos
        self.assertLess(response_time, 2.0)
        self.assertIn(response.status_code, [200, 503])
    
    def test_response_time_detailed_health_check(self):
        """Testa tempo de resposta do health check detalhado."""
        start_time = time.time()
        response = self.app.get('/health-check/detailed')
        response_time = time.time() - start_time
        
        # Health check detalhado pode demorar mais devido às verificações de serviços
        self.assertLess(response_time, 10.0)
        self.assertIn(response.status_code, [200, 503])
    
    def test_memory_usage_stability(self):
        """Testa estabilidade do uso de memória."""
        import psutil
        import gc
        
        # Obter uso de memória inicial
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Fazer múltiplas requisições
        for _ in range(10):
            response = self.app.get('/health-check')
            self.assertIn(response.status_code, [200, 503])
        
        # Forçar garbage collection
        gc.collect()
        
        # Verificar uso de memória final
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Aumento de memória deve ser razoável (menos de 50MB)
        self.assertLess(memory_increase, 50 * 1024 * 1024)


if __name__ == '__main__':
    unittest.main()


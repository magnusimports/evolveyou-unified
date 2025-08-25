"""
Testes unitários para o Health Check Service.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import time
from datetime import datetime, timezone

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import HealthChecker, app


class TestHealthChecker(unittest.TestCase):
    """Testes para a classe HealthChecker."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.health_checker = HealthChecker()
        self.app = app.test_client()
        self.app.testing = True
    
    def test_init(self):
        """Testa a inicialização do HealthChecker."""
        checker = HealthChecker()
        self.assertIsInstance(checker.start_time, float)
        self.assertLessEqual(checker.start_time, time.time())
    
    def test_get_uptime(self):
        """Testa o cálculo do tempo de atividade."""
        # Simular que o serviço está rodando há 10 segundos
        self.health_checker.start_time = time.time() - 10
        uptime = self.health_checker.get_uptime()
        
        self.assertGreaterEqual(uptime, 9.9)  # Permitir pequena margem de erro
        self.assertLessEqual(uptime, 10.1)
    
    @patch('app.psutil.cpu_percent')
    @patch('app.psutil.virtual_memory')
    @patch('app.psutil.disk_usage')
    def test_check_system_resources_healthy(self, mock_disk, mock_memory, mock_cpu):
        """Testa verificação de recursos do sistema em estado saudável."""
        # Configurar mocks para sistema saudável
        mock_cpu.return_value = 30.0
        mock_memory.return_value = Mock(percent=40.0)
        mock_disk.return_value = Mock(percent=50.0)
        
        result = self.health_checker.check_system_resources()
        
        self.assertEqual(result['status'], 'healthy')
        self.assertEqual(result['cpu_percent'], 30.0)
        self.assertEqual(result['memory_percent'], 40.0)
        self.assertEqual(result['disk_percent'], 50.0)
        self.assertEqual(result['warnings'], [])
    
    @patch('app.psutil.cpu_percent')
    @patch('app.psutil.virtual_memory')
    @patch('app.psutil.disk_usage')
    def test_check_system_resources_degraded(self, mock_disk, mock_memory, mock_cpu):
        """Testa verificação de recursos do sistema em estado degradado."""
        # Configurar mocks para sistema degradado
        mock_cpu.return_value = 85.0
        mock_memory.return_value = Mock(percent=85.0)
        mock_disk.return_value = Mock(percent=95.0)
        
        result = self.health_checker.check_system_resources()
        
        self.assertEqual(result['status'], 'degraded')
        self.assertEqual(result['cpu_percent'], 85.0)
        self.assertEqual(result['memory_percent'], 85.0)
        self.assertEqual(result['disk_percent'], 95.0)
        self.assertEqual(len(result['warnings']), 3)
    
    @patch('app.psutil.cpu_percent')
    def test_check_system_resources_exception(self, mock_cpu):
        """Testa verificação de recursos quando ocorre exceção."""
        # Configurar mock para lançar exceção
        mock_cpu.side_effect = Exception("System error")
        
        result = self.health_checker.check_system_resources()
        
        self.assertEqual(result['status'], 'unhealthy')
        self.assertIn('error', result)
        self.assertEqual(result['error'], "System error")
    
    @patch('app.db')
    def test_check_firestore_healthy(self, mock_db):
        """Testa verificação do Firestore em estado saudável."""
        # Configurar mock para Firestore saudável
        mock_doc = Mock()
        mock_doc.get.return_value = Mock(exists=True)
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc
        mock_db.collection.return_value = mock_collection
        
        result = self.health_checker.check_firestore()
        
        self.assertEqual(result['status'], 'healthy')
        self.assertIn('details', result)
        self.assertIn('response_time', result)
    
    @patch('app.db')
    def test_check_firestore_unhealthy(self, mock_db):
        """Testa verificação do Firestore quando não está saudável."""
        # Configurar mock para Firestore com problema
        mock_db.collection.side_effect = Exception("Connection failed")
        
        result = self.health_checker.check_firestore()
        
        self.assertEqual(result['status'], 'unhealthy')
        self.assertIn('error', result)
        self.assertEqual(result['error'], "Connection failed")
    
    @patch('app.requests.get')
    def test_check_service_healthy(self, mock_get):
        """Testa verificação de serviço em estado saudável."""
        # Configurar mock para resposta saudável
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        config = {
            'url': 'http://test-service:8080',
            'timeout': 5
        }
        
        result = self.health_checker.check_service('test-service', config)
        
        self.assertEqual(result['status'], 'healthy')
        self.assertEqual(result['status_code'], 200)
        self.assertIn('response_time', result)
        self.assertIn('url', result)
    
    @patch('app.requests.get')
    def test_check_service_unhealthy_status(self, mock_get):
        """Testa verificação de serviço com status HTTP não saudável."""
        # Configurar mock para resposta com erro
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        config = {
            'url': 'http://test-service:8080',
            'timeout': 5
        }
        
        result = self.health_checker.check_service('test-service', config)
        
        self.assertEqual(result['status'], 'unhealthy')
        self.assertEqual(result['status_code'], 500)
        self.assertIn('error', result)
    
    @patch('app.requests.get')
    def test_check_service_timeout(self, mock_get):
        """Testa verificação de serviço com timeout."""
        # Configurar mock para timeout
        mock_get.side_effect = Exception("Request timeout")
        
        config = {
            'url': 'http://test-service:8080',
            'timeout': 5
        }
        
        result = self.health_checker.check_service('test-service', config)
        
        self.assertEqual(result['status'], 'unhealthy')
        self.assertIn('error', result)


class TestHealthCheckEndpoints(unittest.TestCase):
    """Testes para os endpoints de health check."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Limpar cache entre testes
        import app as app_module
        app_module.health_cache.clear()
    
    @patch('app.health_checker.check_firestore')
    @patch('app.health_checker.check_system_resources')
    def test_health_check_endpoint_healthy(self, mock_system, mock_firestore):
        """Testa endpoint de health check com sistema saudável."""
        # Configurar mocks para sistema saudável
        mock_firestore.return_value = {'status': 'healthy'}
        mock_system.return_value = {'status': 'healthy', 'cpu_percent': 30}
        
        response = self.app.get('/health-check')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('service', data)
        self.assertIn('version', data)
        self.assertIn('timestamp', data)
        self.assertIn('checks', data)
    
    @patch('app.health_checker.check_firestore')
    @patch('app.health_checker.check_system_resources')
    def test_health_check_endpoint_degraded(self, mock_system, mock_firestore):
        """Testa endpoint de health check com sistema degradado."""
        # Configurar mocks para sistema degradado
        mock_firestore.return_value = {'status': 'unhealthy', 'error': 'Connection failed'}
        mock_system.return_value = {'status': 'healthy', 'cpu_percent': 30}
        
        response = self.app.get('/health-check')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)  # Degraded ainda retorna 200
        self.assertEqual(data['status'], 'degraded')
    
    @patch('app.health_checker.check_firestore')
    @patch('app.health_checker.check_system_resources')
    def test_health_check_endpoint_unhealthy(self, mock_system, mock_firestore):
        """Testa endpoint de health check com sistema não saudável."""
        # Configurar mocks para sistema não saudável
        mock_firestore.return_value = {'status': 'unhealthy', 'error': 'Connection failed'}
        mock_system.return_value = {'status': 'unhealthy', 'error': 'High resource usage'}
        
        response = self.app.get('/health-check')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 503)
        self.assertEqual(data['status'], 'unhealthy')
    
    def test_info_endpoint(self):
        """Testa endpoint de informações do serviço."""
        response = self.app.get('/info')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('service', data)
        self.assertIn('version', data)
        self.assertIn('description', data)
        self.assertIn('endpoints', data)
        self.assertIn('uptime_seconds', data)
    
    @patch('app.health_checker.check_system_resources')
    def test_metrics_endpoint(self, mock_system):
        """Testa endpoint de métricas."""
        # Configurar mock para métricas
        mock_system.return_value = {
            'cpu_percent': 45.0,
            'memory_percent': 60.0,
            'disk_percent': 30.0
        }
        
        response = self.app.get('/metrics')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('metrics', data)
        self.assertEqual(data['metrics']['cpu_percent'], 45.0)
        self.assertEqual(data['metrics']['memory_percent'], 60.0)
        self.assertEqual(data['metrics']['disk_percent'], 30.0)
    
    def test_not_found_endpoint(self):
        """Testa endpoint não encontrado."""
        response = self.app.get('/endpoint-inexistente')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'Not Found')
        self.assertIn('message', data)
        self.assertIn('timestamp', data)


if __name__ == '__main__':
    unittest.main()


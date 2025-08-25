"""
Health Check Service - EvolveYou Platform

Este microserviço é responsável por monitorar a saúde de todos os componentes
da infraestrutura EvolveYou, incluindo outros microserviços, banco de dados,
e dependências externas.
"""

import os
import logging
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
import google.cloud.firestore as firestore
import google.cloud.logging
import psutil
import requests

# Configuração de logging
if not os.getenv('FIRESTORE_EMULATOR_HOST'):
    # Apenas em produção, usar Cloud Logging
    client = google.cloud.logging.Client()
    client.setup_logging()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização da aplicação Flask
app = Flask(__name__)
CORS(app, origins="*")  # Permitir CORS para todas as origens

# Configuração do Firestore
if os.getenv('FIRESTORE_EMULATOR_HOST'):
    # Ambiente de desenvolvimento com emulador
    os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv('GOOGLE_CLOUD_PROJECT', 'evolveyou-dev')
    db = firestore.Client()
    logger.info("Conectado ao Firestore Emulator")
else:
    # Ambiente de produção
    db = firestore.Client()
    logger.info("Conectado ao Firestore em produção")

# Configurações da aplicação
SERVICE_NAME = os.getenv('SERVICE_NAME', 'health-check-service')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
PORT = int(os.getenv('PORT', 8080))
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Cache para resultados de health checks
health_cache = {}
cache_ttl = 30  # TTL em segundos

# Configuração de serviços para monitoramento
SERVICES_CONFIG = {
    'auth-service': {
        'url': os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8080'),
        'timeout': 5,
        'critical': True
    },
    'user-service': {
        'url': os.getenv('USER_SERVICE_URL', 'http://user-service:8080'),
        'timeout': 5,
        'critical': True
    },
    'workout-service': {
        'url': os.getenv('WORKOUT_SERVICE_URL', 'http://workout-service:8080'),
        'timeout': 5,
        'critical': True
    },
    'notification-service': {
        'url': os.getenv('NOTIFICATION_SERVICE_URL', 'http://notification-service:8080'),
        'timeout': 5,
        'critical': False
    }
}


class HealthChecker:
    """Classe responsável por executar verificações de saúde."""
    
    def __init__(self):
        self.start_time = time.time()
    
    def check_firestore(self) -> Dict[str, Any]:
        """Verifica conectividade com Firestore."""
        try:
            # Tentar uma operação simples no Firestore
            test_doc = db.collection('health_checks').document('test')
            test_doc.set({
                'timestamp': datetime.now(timezone.utc),
                'service': SERVICE_NAME
            })
            
            # Tentar ler o documento
            doc = test_doc.get()
            if doc.exists:
                return {
                    'status': 'healthy',
                    'response_time': 0.1,  # Placeholder
                    'details': 'Firestore connection successful'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Document not found after write'
                }
                
        except Exception as e:
            logger.error(f"Firestore health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Verifica recursos do sistema."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determinar status baseado nos recursos
            status = 'healthy'
            warnings = []
            
            if cpu_percent > 80:
                status = 'degraded'
                warnings.append(f'High CPU usage: {cpu_percent}%')
            
            if memory.percent > 80:
                status = 'degraded'
                warnings.append(f'High memory usage: {memory.percent}%')
            
            if disk.percent > 90:
                status = 'degraded'
                warnings.append(f'High disk usage: {disk.percent}%')
            
            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'warnings': warnings
            }
            
        except Exception as e:
            logger.error(f"System resources check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_service(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica saúde de um microserviço específico."""
        try:
            start_time = time.time()
            
            # Fazer requisição para o health check do serviço
            health_url = f"{config['url']}/health-check"
            response = requests.get(
                health_url,
                timeout=config['timeout'],
                headers={'User-Agent': f'{SERVICE_NAME}/{SERVICE_VERSION}'}
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': round(response_time, 3),
                    'status_code': response.status_code,
                    'url': health_url
                }
            else:
                return {
                    'status': 'unhealthy',
                    'response_time': round(response_time, 3),
                    'status_code': response.status_code,
                    'url': health_url,
                    'error': f'HTTP {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'unhealthy',
                'error': 'Request timeout',
                'url': config['url']
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'unhealthy',
                'error': 'Connection failed',
                'url': config['url']
            }
        except Exception as e:
            logger.error(f"Service check failed for {service_name}: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'url': config['url']
            }
    
    def get_uptime(self) -> float:
        """Retorna o tempo de atividade do serviço em segundos."""
        return time.time() - self.start_time


# Instância global do health checker
health_checker = HealthChecker()


@app.route('/health-check', methods=['GET'])
def health_check() -> tuple[Dict[str, Any], int]:
    """
    Endpoint principal de verificação de saúde.
    
    Returns:
        Tuple contendo resposta JSON e código de status HTTP
    """
    try:
        # Verificar cache
        cache_key = 'basic_health'
        current_time = time.time()
        
        if cache_key in health_cache:
            cached_result, cache_time = health_cache[cache_key]
            if current_time - cache_time < cache_ttl:
                return cached_result, cached_result.get('status_code', 200)
        
        # Executar verificações básicas
        checks = {}
        overall_status = 'healthy'
        
        # Verificar Firestore
        firestore_check = health_checker.check_firestore()
        checks['firestore'] = firestore_check
        if firestore_check['status'] != 'healthy':
            overall_status = 'degraded'
        
        # Verificar recursos do sistema
        system_check = health_checker.check_system_resources()
        checks['system'] = system_check
        if system_check['status'] == 'degraded' and overall_status == 'healthy':
            overall_status = 'degraded'
        elif system_check['status'] == 'unhealthy':
            overall_status = 'unhealthy'
        
        # Preparar resposta
        response = {
            'status': overall_status,
            'service': SERVICE_NAME,
            'version': SERVICE_VERSION,
            'environment': ENVIRONMENT,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'uptime_seconds': round(health_checker.get_uptime(), 2),
            'checks': checks
        }
        
        # Determinar código de status HTTP
        status_code = 200 if overall_status in ['healthy', 'degraded'] else 503
        response['status_code'] = status_code
        
        # Atualizar cache
        health_cache[cache_key] = (response, current_time)
        
        logger.info(f"Health check completed: {overall_status}")
        return response, status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        error_response = {
            'status': 'unhealthy',
            'service': SERVICE_NAME,
            'version': SERVICE_VERSION,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e),
            'status_code': 500
        }
        
        return error_response, 500


@app.route('/health-check/detailed', methods=['GET'])
def detailed_health_check() -> tuple[Dict[str, Any], int]:
    """
    Endpoint de verificação de saúde detalhada.
    Inclui verificação de todos os microserviços.
    
    Returns:
        Tuple contendo resposta JSON e código de status HTTP
    """
    try:
        # Verificar cache
        cache_key = 'detailed_health'
        current_time = time.time()
        
        if cache_key in health_cache:
            cached_result, cache_time = health_cache[cache_key]
            if current_time - cache_time < cache_ttl:
                return cached_result, cached_result.get('status_code', 200)
        
        # Executar verificações básicas
        checks = {}
        overall_status = 'healthy'
        critical_failures = 0
        
        # Verificar Firestore
        firestore_check = health_checker.check_firestore()
        checks['firestore'] = firestore_check
        if firestore_check['status'] != 'healthy':
            overall_status = 'degraded'
            critical_failures += 1
        
        # Verificar recursos do sistema
        system_check = health_checker.check_system_resources()
        checks['system'] = system_check
        if system_check['status'] == 'degraded' and overall_status == 'healthy':
            overall_status = 'degraded'
        elif system_check['status'] == 'unhealthy':
            overall_status = 'unhealthy'
            critical_failures += 1
        
        # Verificar microserviços
        services_status = {}
        for service_name, config in SERVICES_CONFIG.items():
            service_check = health_checker.check_service(service_name, config)
            services_status[service_name] = service_check
            
            if service_check['status'] != 'healthy':
                if config['critical']:
                    critical_failures += 1
                    overall_status = 'degraded'
                else:
                    # Serviços não críticos não afetam o status geral
                    pass
        
        checks['services'] = services_status
        
        # Determinar status final
        if critical_failures > 2:
            overall_status = 'unhealthy'
        
        # Preparar resposta
        response = {
            'status': overall_status,
            'service': SERVICE_NAME,
            'version': SERVICE_VERSION,
            'environment': ENVIRONMENT,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'uptime_seconds': round(health_checker.get_uptime(), 2),
            'critical_failures': critical_failures,
            'checks': checks,
            'summary': {
                'total_services': len(SERVICES_CONFIG),
                'healthy_services': len([s for s in services_status.values() if s['status'] == 'healthy']),
                'unhealthy_services': len([s for s in services_status.values() if s['status'] == 'unhealthy'])
            }
        }
        
        # Determinar código de status HTTP
        status_code = 200 if overall_status in ['healthy', 'degraded'] else 503
        response['status_code'] = status_code
        
        # Atualizar cache
        health_cache[cache_key] = (response, current_time)
        
        logger.info(f"Detailed health check completed: {overall_status}")
        return response, status_code
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        
        error_response = {
            'status': 'unhealthy',
            'service': SERVICE_NAME,
            'version': SERVICE_VERSION,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e),
            'status_code': 500
        }
        
        return error_response, 500


@app.route('/metrics', methods=['GET'])
def metrics() -> Dict[str, Any]:
    """
    Endpoint que retorna métricas básicas do serviço.
    
    Returns:
        Dicionário com métricas do serviço
    """
    try:
        system_info = health_checker.check_system_resources()
        
        return {
            'service': SERVICE_NAME,
            'version': SERVICE_VERSION,
            'uptime_seconds': round(health_checker.get_uptime(), 2),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': {
                'cpu_percent': system_info.get('cpu_percent', 0),
                'memory_percent': system_info.get('memory_percent', 0),
                'disk_percent': system_info.get('disk_percent', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        return {
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }, 500


@app.route('/info', methods=['GET'])
def service_info() -> Dict[str, Any]:
    """
    Endpoint que retorna informações sobre o serviço.
    
    Returns:
        Dicionário com informações do serviço
    """
    return {
        'service': SERVICE_NAME,
        'version': SERVICE_VERSION,
        'environment': ENVIRONMENT,
        'description': 'Health Check Service para monitoramento da infraestrutura EvolveYou',
        'endpoints': [
            '/health-check',
            '/health-check/detailed',
            '/metrics',
            '/info'
        ],
        'uptime_seconds': round(health_checker.get_uptime(), 2),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'monitored_services': list(SERVICES_CONFIG.keys())
    }


@app.errorhandler(404)
def not_found(error) -> tuple[Dict[str, Any], int]:
    """Handler para erros 404."""
    return {
        'error': 'Not Found',
        'message': 'O endpoint solicitado não foi encontrado',
        'service': SERVICE_NAME,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'path': request.path
    }, 404


@app.errorhandler(500)
def internal_error(error) -> tuple[Dict[str, Any], int]:
    """Handler para erros 500."""
    logger.error(f"Internal server error: {str(error)}")
    
    return {
        'error': 'Internal Server Error',
        'message': 'Ocorreu um erro interno no servidor',
        'service': SERVICE_NAME,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'path': request.path
    }, 500


@app.before_request
def log_request_info():
    """Log de informações da requisição."""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")


@app.after_request
def log_response_info(response):
    """Log de informações da resposta."""
    logger.info(f"Response: {response.status_code}")
    return response


if __name__ == '__main__':
    logger.info(f"Iniciando {SERVICE_NAME} v{SERVICE_VERSION} na porta {PORT}")
    logger.info(f"Ambiente: {ENVIRONMENT}")
    logger.info(f"Monitorando {len(SERVICES_CONFIG)} serviços")
    
    app.run(host='0.0.0.0', port=PORT, debug=(ENVIRONMENT == 'development'))


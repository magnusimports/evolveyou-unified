# Health Check Service - EvolveYou

O Health Check Service é um microserviço responsável por monitorar a saúde de todos os componentes da infraestrutura EvolveYou, incluindo outros microserviços, banco de dados e dependências externas.

## Funcionalidades

- **Monitoramento de Saúde**: Verifica o status de todos os microserviços da plataforma
- **Verificação de Recursos**: Monitora CPU, memória e espaço em disco
- **Conectividade de Banco**: Testa conexão com Firestore
- **Cache Inteligente**: Cache de resultados para melhor performance
- **Métricas Detalhadas**: Fornece métricas de sistema e performance
- **Alertas Automáticos**: Integração com sistema de monitoramento do GCP

## Endpoints

### `GET /health-check`
Verificação básica de saúde do serviço.

**Resposta de Exemplo:**
```json
{
  "status": "healthy",
  "service": "health-check-service",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2025-01-08T10:30:00Z",
  "uptime_seconds": 3600.5,
  "checks": {
    "firestore": {
      "status": "healthy",
      "response_time": 0.1,
      "details": "Firestore connection successful"
    },
    "system": {
      "status": "healthy",
      "cpu_percent": 25.3,
      "memory_percent": 45.2,
      "disk_percent": 60.1,
      "warnings": []
    }
  }
}
```

### `GET /health-check/detailed`
Verificação detalhada incluindo todos os microserviços.

**Resposta de Exemplo:**
```json
{
  "status": "healthy",
  "service": "health-check-service",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2025-01-08T10:30:00Z",
  "uptime_seconds": 3600.5,
  "critical_failures": 0,
  "checks": {
    "firestore": { "status": "healthy" },
    "system": { "status": "healthy" },
    "services": {
      "auth-service": {
        "status": "healthy",
        "response_time": 0.2,
        "status_code": 200,
        "url": "http://auth-service:8080/health-check"
      },
      "user-service": {
        "status": "healthy",
        "response_time": 0.15,
        "status_code": 200,
        "url": "http://user-service:8080/health-check"
      }
    }
  },
  "summary": {
    "total_services": 4,
    "healthy_services": 4,
    "unhealthy_services": 0
  }
}
```

### `GET /metrics`
Métricas básicas do serviço.

**Resposta de Exemplo:**
```json
{
  "service": "health-check-service",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "timestamp": "2025-01-08T10:30:00Z",
  "metrics": {
    "cpu_percent": 25.3,
    "memory_percent": 45.2,
    "disk_percent": 60.1
  }
}
```

### `GET /info`
Informações sobre o serviço.

**Resposta de Exemplo:**
```json
{
  "service": "health-check-service",
  "version": "1.0.0",
  "environment": "production",
  "description": "Health Check Service para monitoramento da infraestrutura EvolveYou",
  "endpoints": [
    "/health-check",
    "/health-check/detailed",
    "/metrics",
    "/info"
  ],
  "uptime_seconds": 3600.5,
  "timestamp": "2025-01-08T10:30:00Z",
  "monitored_services": [
    "auth-service",
    "user-service",
    "workout-service",
    "notification-service"
  ]
}
```

## Status de Saúde

O serviço retorna três possíveis status:

- **healthy**: Todos os sistemas funcionando normalmente
- **degraded**: Alguns problemas detectados, mas serviço ainda funcional
- **unhealthy**: Problemas críticos detectados

### Códigos de Status HTTP

- `200`: Sistema saudável ou degradado
- `503`: Sistema não saudável
- `404`: Endpoint não encontrado
- `500`: Erro interno do servidor

## Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `SERVICE_NAME` | Nome do serviço | `health-check-service` |
| `SERVICE_VERSION` | Versão do serviço | `1.0.0` |
| `PORT` | Porta do serviço | `8080` |
| `ENVIRONMENT` | Ambiente de execução | `development` |
| `GOOGLE_CLOUD_PROJECT` | ID do projeto GCP | - |
| `FIRESTORE_EMULATOR_HOST` | Host do emulador Firestore | - |
| `AUTH_SERVICE_URL` | URL do serviço de autenticação | `http://auth-service:8080` |
| `USER_SERVICE_URL` | URL do serviço de usuários | `http://user-service:8080` |
| `WORKOUT_SERVICE_URL` | URL do serviço de treinos | `http://workout-service:8080` |
| `NOTIFICATION_SERVICE_URL` | URL do serviço de notificações | `http://notification-service:8080` |

## Desenvolvimento Local

### Pré-requisitos

- Python 3.11+
- Docker (opcional)
- Firestore Emulator (para testes)

### Instalação

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variáveis de ambiente:**
   ```bash
   export FIRESTORE_EMULATOR_HOST=localhost:8080
   export GOOGLE_CLOUD_PROJECT=evolveyou-dev
   export ENVIRONMENT=development
   ```

3. **Executar o serviço:**
   ```bash
   python src/app.py
   ```

### Executar com Docker

1. **Construir imagem:**
   ```bash
   docker build -t health-check-service .
   ```

2. **Executar container:**
   ```bash
   docker run -p 8080:8080 \
     -e FIRESTORE_EMULATOR_HOST=host.docker.internal:8080 \
     -e GOOGLE_CLOUD_PROJECT=evolveyou-dev \
     health-check-service
   ```

## Testes

### Testes Unitários

```bash
python -m pytest tests/unit/ -v
```

### Testes de Integração

```bash
# Iniciar Firestore Emulator
gcloud beta emulators firestore start --host-port=localhost:8080 &

# Executar testes
python -m pytest tests/integration/ -v
```

### Cobertura de Código

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## Deploy

### Google Cloud Run

1. **Construir e enviar imagem:**
   ```bash
   gcloud builds submit --tag us-central1-docker.pkg.dev/evolveyou-prod/evolveyou-containers/health-check-service
   ```

2. **Deploy no Cloud Run:**
   ```bash
   gcloud run deploy health-check-service \
     --image us-central1-docker.pkg.dev/evolveyou-prod/evolveyou-containers/health-check-service \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Usando GitHub Actions

O deploy é automatizado via GitHub Actions quando há push para a branch `main`. Veja `.github/workflows/deploy-template.yml`.

## Monitoramento

### Métricas Disponíveis

- **Latência**: Tempo de resposta dos endpoints
- **Taxa de Erro**: Porcentagem de requisições com erro
- **Throughput**: Requisições por segundo
- **Recursos**: CPU, memória e disco
- **Uptime**: Tempo de atividade do serviço

### Alertas

O serviço está configurado para enviar alertas quando:

- Taxa de erro > 5%
- Latência > 2 segundos
- CPU > 80%
- Memória > 80%
- Disco > 90%

### Dashboards

Dashboards estão disponíveis no Google Cloud Monitoring para visualização das métricas.

## Cache

O serviço implementa cache para melhorar performance:

- **TTL**: 30 segundos
- **Tipos**: Health check básico e detalhado
- **Invalidação**: Automática por tempo

## Segurança

### Autenticação

- Endpoints públicos (não requerem autenticação)
- Acesso restrito via API Gateway em produção

### Autorização

- Service Account específico para acesso ao Firestore
- Princípio do menor privilégio

### Logs

- Logs estruturados em JSON
- Integração com Google Cloud Logging
- Não loggar informações sensíveis

## Troubleshooting

### Problemas Comuns

1. **Firestore Connection Failed**
   - Verificar se o emulador está rodando (desenvolvimento)
   - Verificar credenciais do Service Account (produção)

2. **High Resource Usage**
   - Verificar se há vazamentos de memória
   - Analisar logs para operações custosas

3. **Service Timeout**
   - Verificar conectividade de rede
   - Aumentar timeout se necessário

### Logs Úteis

```bash
# Ver logs em tempo real
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=health-check-service" --limit 50 --format json

# Filtrar por erro
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=health-check-service AND severity>=ERROR" --limit 20
```

## Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto é propriedade da EvolveYou. Todos os direitos reservados.


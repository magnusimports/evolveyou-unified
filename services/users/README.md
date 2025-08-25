# EvolveYou Users Service

Microserviço responsável pela gestão completa de usuários da plataforma EvolveYou, incluindo autenticação, onboarding personalizado e cálculo de metas calóricas.

## 🚀 Funcionalidades Principais

### 🔐 Autenticação Robusta
- **Registro tradicional**: Email/senha com validações rigorosas
- **Login social**: Google, Apple, Facebook
- **JWT tokens**: Access + refresh tokens seguros
- **Rate limiting**: Proteção contra ataques
- **Criptografia**: Senhas com bcrypt

### 📋 Onboarding Inteligente
- **Anamnese médica completa**: Dados de saúde, histórico médico
- **Avaliação de estilo de vida**: Atividade, sono, stress
- **Objetivos fitness**: Metas personalizadas e realistas
- **Validações científicas**: Ranges fisiológicos seguros

### 🧮 Algoritmo Calórico Científico
- **Fórmula Mifflin-St Jeor**: Padrão ouro para BMR
- **Fatores personalizados**: Composição corporal, suplementação, experiência
- **TDEE preciso**: Combinação trabalho + lazer
- **Metas calóricas**: Cutting (-20%), Bulking (+15%), Manutenção
- **Macronutrientes**: Distribuição otimizada por objetivo

### 🔄 Comunicação Entre Serviços
- **Eventos automáticos**: Notifica outros serviços
- **Health checks**: Monitora conectividade
- **Retry logic**: Tratamento de falhas
- **Auditoria**: Logs completos de comunicação

## 📊 Endpoints da API

### Autenticação
```http
POST /auth/register          # Registrar novo usuário
POST /auth/login             # Login com email/senha
POST /auth/social-login      # Login social (Google/Apple/Facebook)
POST /auth/refresh           # Renovar tokens JWT
POST /auth/logout            # Logout e invalidar tokens
```

### Onboarding
```http
POST /onboarding/submit      # Submeter dados completos do onboarding
GET  /onboarding/status      # Status do onboarding do usuário
PUT  /onboarding/step        # Atualizar etapa específica
```

### Perfil de Usuário
```http
GET  /users/me               # Obter perfil completo
PUT  /users/me               # Atualizar perfil
GET  /users/me/calories      # Obter cálculos calóricos
PUT  /users/me/goals         # Atualizar objetivos
```

### Sistema
```http
GET  /health                 # Health check do serviço
GET  /metrics                # Métricas de performance
```

## 🛠️ Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **Pydantic**: Validação de dados robusta
- **Firebase Admin**: Integração com Firestore
- **JWT**: Autenticação stateless
- **bcrypt**: Criptografia de senhas
- **pytest**: Testes unitários e integração
- **uvicorn**: Servidor ASGI de alta performance

## 📦 Instalação e Configuração

### Pré-requisitos
- Python 3.11+
- Firebase project configurado
- Variáveis de ambiente configuradas

### Instalação
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações
```

### Variáveis de Ambiente Obrigatórias
```env
# Firebase
FIREBASE_PROJECT_ID=evolveyou-23580
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Ambiente
ENVIRONMENT=development
DEBUG=false
PORT=8080
```

### Executar Localmente
```bash
# Modo desenvolvimento
cd src
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Modo produção
uvicorn main:app --host 0.0.0.0 --port 8080
```

## 🧪 Testes

### Executar Testes
```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_auth_service.py -v
pytest tests/test_calorie_service.py -v

# Com cobertura
pytest tests/ --cov=src --cov-report=html
```

### Cobertura de Testes
- **Autenticação**: 95%+ cobertura
- **Cálculo calórico**: 90%+ cobertura
- **Onboarding**: 85%+ cobertura
- **Comunicação**: 80%+ cobertura

## 🔧 Algoritmo Calórico Detalhado

### 1. BMR Base (Mifflin-St Jeor)
```python
# Homens
BMR = 10 × peso(kg) + 6.25 × altura(cm) - 5 × idade + 5

# Mulheres  
BMR = 10 × peso(kg) + 6.25 × altura(cm) - 5 × idade - 161
```

### 2. Fatores de Ajuste

#### Composição Corporal
- **Muito baixo** (<10% H, <16% M): 0.85
- **Baixo** (10-15% H, 16-20% M): 0.90
- **Normal** (15-20% H, 20-25% M): 1.0
- **Alto** (20-25% H, 25-30% M): 1.05
- **Muito alto** (>25% H, >30% M): 1.10

#### Suplementação (Pharma Factor)
- **Termogênico**: +5%
- **Cafeína**: +3%
- **Pré-treino**: +4%
- **Creatina**: +2%
- **Whey protein**: +1%

#### Experiência de Treinamento
- **Iniciante** (0-6 meses): 0.95
- **Intermediário** (6 meses - 2 anos): 1.0
- **Avançado** (2-5 anos): 1.05
- **Expert** (>5 anos): 1.10

### 3. Fator de Atividade
- **Sedentário**: 1.2
- **Levemente ativo**: 1.375
- **Moderadamente ativo**: 1.55
- **Muito ativo**: 1.725
- **Extremamente ativo**: 1.9

### 4. Cálculo Final
```python
TDEE = BMR × body_composition_factor × pharma_factor × training_factor × activity_factor

# Metas calóricas
maintenance_calories = TDEE
cutting_calories = TDEE × 0.8  # -20%
bulking_calories = TDEE × 1.15  # +15%
```

### 5. Distribuição de Macronutrientes
```python
# Proteína: 2.2g/kg peso corporal
protein_grams = weight_kg × 2.2

# Gordura: 25% das calorias
fat_grams = (target_calories × 0.25) / 9

# Carboidratos: restante das calorias
carbs_grams = (target_calories - (protein_grams × 4) - (fat_grams × 9)) / 4
```

## 🔒 Segurança

### Validações Implementadas
- **Email único**: Verificação no Firebase
- **Senha forte**: 8+ chars, maiúscula, minúscula, número, símbolo
- **Rate limiting**: 5 tentativas/5min para registro, 10/5min para login
- **JWT seguro**: Tokens com expiração e refresh
- **Dados médicos**: Validação de ranges fisiológicos

### Proteções Ativas
- **CORS configurado**: Origins permitidos definidos
- **Headers de segurança**: Proteção contra XSS, CSRF
- **Logs de auditoria**: Todas as ações críticas logadas
- **Sanitização**: Inputs validados e sanitizados

## 📈 Performance

### Otimizações Implementadas
- **Cache em memória**: Configurações e dados frequentes
- **Conexão pool**: Firebase com reutilização de conexões
- **Validação assíncrona**: Processamento não-bloqueante
- **Logs estruturados**: JSON para análise eficiente

### Métricas Esperadas
- **Latência média**: <100ms para endpoints simples
- **Throughput**: 1000+ req/s em produção
- **Disponibilidade**: 99.9% uptime
- **Escalabilidade**: Auto-scaling no Cloud Run

## 🚀 Deploy

### Docker
```bash
# Build da imagem
docker build -t users-service .

# Executar container
docker run -p 8080:8080 --env-file .env users-service
```

### Cloud Run
```bash
# Deploy via gcloud
gcloud run deploy users-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### GitHub Actions
O deploy é automatizado via GitHub Actions quando há push para `main`:
1. Build da imagem Docker
2. Push para Artifact Registry
3. Deploy no Cloud Run
4. Testes de smoke

## 📚 Documentação Adicional

- **OpenAPI Spec**: `/docs` (Swagger UI)
- **ReDoc**: `/redoc` (Documentação alternativa)
- **Health Check**: `/health` (Status do serviço)
- **Métricas**: `/metrics` (Prometheus format)

## 🤝 Contribuição

### Padrões de Código
- **Black**: Formatação automática
- **isort**: Organização de imports
- **flake8**: Linting
- **mypy**: Type checking

### Workflow de Desenvolvimento
1. Fork do repositório
2. Criar branch feature
3. Implementar mudanças
4. Executar testes
5. Criar Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- **Email**: dev@evolveyou.com.br
- **Slack**: #users-service
- **Issues**: GitHub Issues

## 📄 Licença

Proprietary - EvolveYou © 2025

---

**EvolveYou Users Service** - Transformando vidas através da tecnologia fitness! 💪🚀


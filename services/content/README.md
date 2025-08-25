# EvolveYou Content Service

Microserviço responsável por gerenciar dados de alimentos e exercícios da plataforma EvolveYou.

## 🚀 Características

- **Busca Avançada**: Filtros múltiplos para alimentos e exercícios
- **Dados Nutricionais**: Informações completas por 100g e porções
- **Orientações Premium**: Conteúdo exclusivo para usuários pagantes
- **Cálculo Calórico**: Valores MET para estimativa de gasto energético
- **Cache Inteligente**: Otimização de performance
- **API RESTful**: Endpoints padronizados e documentados

## 📋 Pré-requisitos

- Python 3.11+
- Firebase Admin SDK configurado
- Projeto Firebase/Firestore ativo

## 🛠️ Instalação

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Configurar variáveis de ambiente:**
```bash
cp .env.example .env
# Editar .env com suas configurações
```

3. **Configurar Firebase:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
export FIREBASE_PROJECT_ID=evolveyou-23580
```

## 🚀 Execução

### Desenvolvimento Local

```bash
# Definir PYTHONPATH
export PYTHONPATH=/path/to/content-service/src

# Executar servidor
cd src
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### Docker

```bash
# Build da imagem
docker build -t content-service .

# Executar container
docker run -p 8080:8080 \
  -e FIREBASE_PROJECT_ID=evolveyou-23580 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/serviceAccountKey.json \
  -v /path/to/serviceAccountKey.json:/app/serviceAccountKey.json \
  content-service
```

### Cloud Run

```bash
# Deploy para Google Cloud Run
gcloud run deploy content-service \
  --image gcr.io/evolveyou-prod/content-service \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=evolveyou-23580
```

## 📚 Endpoints da API

### Health Check
- `GET /health` - Verificação de saúde do serviço

### Alimentos
- `GET /foods` - Buscar alimentos com filtros
- `GET /foods/{food_id}` - Obter alimento por ID

### Exercícios
- `GET /exercises` - Buscar exercícios com filtros
- `GET /exercises/{exercise_id}` - Obter exercício por ID
- `GET /exercises/met-values` - Obter valores MET

### Categorias
- `GET /categories/foods` - Categorias de alimentos
- `GET /categories/exercises` - Categorias de exercícios

## 📖 Documentação

- **API Docs**: http://localhost:8080/docs (Swagger UI)
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI Spec**: `/docs/content-service-openapi.yml`

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/test_main.py -v

# Testes de integração (requer Firebase)
pytest -m integration
```

## 🗄️ Banco de Dados

### Popular Dados Iniciais

```bash
# Executar script de população
python scripts/populate_database.py
```

### Estrutura das Coleções

#### Foods (Alimentos)
```json
{
  "name": "string",
  "category": "string",
  "nutritional_info": {
    "calories": "number",
    "protein": "number",
    "carbs": "number",
    "fat": "number"
  },
  "serving_sizes": [...]
}
```

#### Exercises (Exercícios)
```json
{
  "name": "string",
  "primary_muscle_group": "string",
  "exercise_type": "string",
  "equipment": ["string"],
  "difficulty": "string",
  "premium_guidance": {...}
}
```

#### MET Values
```json
{
  "activity": "string",
  "met_value": "number",
  "exercise_type": "string",
  "intensity": "string"
}
```

## 🔒 Segurança

### Regras Firestore

As regras de segurança estão definidas em `firestore.rules`:

- **Alimentos**: Leitura pública, escrita apenas admins
- **Exercícios**: Leitura pública, orientações premium restritas
- **Dados de usuário**: Acesso apenas ao próprio usuário

### Autenticação

```bash
# Header de autenticação
Authorization: Bearer <firebase_jwt_token>
```

## 📊 Monitoramento

### Métricas Disponíveis

- Latência por endpoint
- Taxa de erro
- Throughput
- Cache hit rate

### Logs Estruturados

```json
{
  "timestamp": "2025-08-09T17:30:00Z",
  "level": "INFO",
  "message": "Busca realizada",
  "search": "frango",
  "results_count": 5
}
```

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `ENVIRONMENT` | Ambiente (dev/prod) | `development` |
| `DEBUG` | Modo debug | `false` |
| `PORT` | Porta do servidor | `8080` |
| `FIREBASE_PROJECT_ID` | ID do projeto Firebase | - |
| `CACHE_TTL` | TTL do cache (segundos) | `3600` |
| `RATE_LIMIT_REQUESTS` | Limite de requests | `100` |

### Cache

O serviço implementa cache em múltiplas camadas:

- **Aplicação**: TTL de 1 hora
- **Query**: 15 minutos
- **Documento**: 2 horas

## 🚨 Troubleshooting

### Problemas Comuns

#### Erro: Firebase não inicializado
```bash
# Verificar credenciais
echo $GOOGLE_APPLICATION_CREDENTIALS
echo $FIREBASE_PROJECT_ID
```

#### Erro: Módulo não encontrado
```bash
# Configurar PYTHONPATH
export PYTHONPATH=/path/to/content-service/src
```

#### Performance lenta
```bash
# Verificar cache
curl http://localhost:8080/health
```

### Logs de Debug

```bash
# Habilitar logs detalhados
export LOG_LEVEL=DEBUG
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### Padrões de Código

- **Linting**: `flake8`
- **Formatação**: `black`
- **Imports**: `isort`
- **Type hints**: Obrigatório

```bash
# Executar linting
flake8 src/
black src/
isort src/
```

## 📄 Licença

Este projeto é propriedade da EvolveYou. Todos os direitos reservados.

## 📞 Suporte

- **Email**: api@evolveyou.com.br
- **Docs**: https://docs.evolveyou.com.br
- **Issues**: GitHub Issues

---

**Desenvolvido com ❤️ pela equipe EvolveYou**


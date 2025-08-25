# EvolveYou Content Service - Documentação da API

## Visão Geral

O **Content Service** é um microserviço fundamental da plataforma EvolveYou, responsável por gerenciar e fornecer dados de alimentos e exercícios. Este serviço oferece endpoints otimizados para busca, filtragem e recuperação de informações nutricionais e de exercícios, suportando tanto usuários gratuitos quanto premium.

### Características Principais

- **Busca Avançada**: Filtros múltiplos para alimentos e exercícios
- **Dados Nutricionais Completos**: Informações detalhadas por 100g e porções
- **Orientações Premium**: Conteúdo exclusivo para usuários pagantes
- **Cálculo Calórico**: Valores MET para estimativa de gasto energético
- **Cache Inteligente**: Otimização de performance com TTL configurável
- **Documentação OpenAPI**: Especificação completa para integração

## Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │────│  Content Service │────│   Firestore     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Cache Layer    │
                       └──────────────────┘
```

### Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e performático
- **Firebase Firestore**: Banco de dados NoSQL escalável
- **Pydantic**: Validação e serialização de dados
- **Structlog**: Logging estruturado para observabilidade
- **Pytest**: Framework de testes abrangente

## Endpoints da API

### Health Check

#### `GET /health`

Endpoint para verificação de saúde do serviço.

**Resposta:**
```json
{
  "status": "healthy",
  "service": "content-service",
  "version": "1.0.0"
}
```

### Alimentos

#### `GET /foods`

Buscar alimentos com filtros avançados e paginação.

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `search` | string | Não | Termo de busca no nome do alimento |
| `category` | string | Não | Categoria do alimento (frutas, carnes, etc.) |
| `min_protein` | float | Não | Proteína mínima por 100g |
| `max_calories` | float | Não | Calorias máximas por 100g |
| `limit` | integer | Não | Limite de resultados (1-100, padrão: 20) |
| `offset` | integer | Não | Offset para paginação (padrão: 0) |

**Exemplo de Requisição:**
```bash
GET /foods?search=frango&category=carnes&min_protein=20&limit=10
```

**Resposta:**
```json
{
  "foods": [
    {
      "id": "food_123",
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
        }
      ],
      "tags": ["proteina", "magro", "ave"],
      "verified": true
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0,
  "has_more": false
}
```

#### `GET /foods/{food_id}`

Obter detalhes completos de um alimento específico.

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `food_id` | string | ID único do alimento |

**Resposta:** Objeto `Food` completo com todas as informações.

### Exercícios

#### `GET /exercises`

Buscar exercícios com filtros avançados.

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `search` | string | Não | Termo de busca no nome do exercício |
| `muscle_group` | string | Não | Grupo muscular (peito, costas, pernas, etc.) |
| `equipment` | string | Não | Equipamento (halteres, barra, peso_corporal, etc.) |
| `difficulty` | string | Não | Nível (iniciante, intermediario, avancado) |
| `exercise_type` | string | Não | Tipo (forca, cardio, flexibilidade) |
| `limit` | integer | Não | Limite de resultados (1-100, padrão: 20) |
| `offset` | integer | Não | Offset para paginação (padrão: 0) |

**Exemplo de Requisição:**
```bash
GET /exercises?muscle_group=peito&equipment=halteres&difficulty=intermediario
```

**Resposta:**
```json
{
  "exercises": [
    {
      "id": "exercise_456",
      "name": "Supino com Halteres",
      "primary_muscle_group": "peito",
      "secondary_muscle_groups": ["triceps", "ombros"],
      "exercise_type": "forca",
      "equipment": ["halteres", "banco"],
      "difficulty": "intermediario",
      "description": "Exercício fundamental para desenvolvimento do peitoral",
      "instructions": [
        "Deite no banco com halteres nas mãos",
        "Posicione os halteres acima do peito",
        "Desça controladamente até sentir alongamento",
        "Empurre os halteres de volta à posição inicial"
      ],
      "premium_guidance": {
        "form_tips": [
          "Mantenha os ombros retraídos",
          "Controle a fase excêntrica"
        ],
        "common_mistakes": [
          "Descer os halteres muito rápido",
          "Não manter amplitude completa"
        ],
        "breathing_pattern": "Inspire na descida, expire na subida"
      },
      "met_value": 6.0,
      "tags": ["peito", "forca", "halteres"]
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

#### `GET /exercises/{exercise_id}`

Obter detalhes completos de um exercício específico.

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `exercise_id` | string | ID único do exercício |

**Resposta:** Objeto `Exercise` completo com orientações premium (se aplicável).

#### `GET /exercises/met-values`

Obter valores MET para cálculo de gasto calórico.

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `exercise_type` | string | Não | Filtrar por tipo (cardio, forca, etc.) |

**Resposta:**
```json
[
  {
    "activity": "Musculação - intensidade moderada",
    "met_value": 3.5,
    "exercise_type": "forca",
    "intensity": "moderada",
    "description": "Exercícios de força com pesos moderados"
  },
  {
    "activity": "Corrida - 8 km/h",
    "met_value": 8.3,
    "exercise_type": "cardio",
    "intensity": "moderada",
    "description": "Corrida em ritmo moderado"
  }
]
```

### Categorias

#### `GET /categories/foods`

Obter lista de categorias de alimentos disponíveis.

**Resposta:**
```json
{
  "categories": [
    "frutas",
    "vegetais",
    "carnes",
    "peixes",
    "laticínios",
    "cereais",
    "leguminosas",
    "oleaginosas",
    "bebidas",
    "doces"
  ]
}
```

#### `GET /categories/exercises`

Obter listas de categorias de exercícios disponíveis.

**Resposta:**
```json
{
  "muscle_groups": [
    "peito", "costas", "ombros", "biceps", "triceps",
    "core", "quadriceps", "isquiotibiais", "gluteos", "panturrilhas"
  ],
  "exercise_types": [
    "forca", "cardio", "flexibilidade", "equilibrio", "funcional"
  ],
  "equipment": [
    "peso_corporal", "halteres", "barra", "kettlebell",
    "elastico", "maquina", "cabo", "medicine_ball"
  ],
  "difficulties": [
    "iniciante", "intermediario", "avancado"
  ]
}
```

## Modelos de Dados

### Food (Alimento)

```json
{
  "id": "string",
  "name": "string",
  "name_en": "string",
  "category": "string",
  "subcategory": "string",
  "brand": "string",
  "barcode": "string",
  "nutritional_info": {
    "calories": "number",
    "protein": "number",
    "carbs": "number",
    "fat": "number",
    "fiber": "number",
    "sugar": "number",
    "sodium": "number",
    "calcium": "number",
    "iron": "number",
    "vitamin_c": "number",
    "vitamin_a": "number"
  },
  "serving_sizes": [
    {
      "name": "string",
      "weight_grams": "number",
      "calories": "number",
      "protein": "number",
      "carbs": "number",
      "fat": "number"
    }
  ],
  "description": "string",
  "ingredients": ["string"],
  "allergens": ["string"],
  "tags": ["string"],
  "source": "string",
  "verified": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Exercise (Exercício)

```json
{
  "id": "string",
  "name": "string",
  "name_en": "string",
  "primary_muscle_group": "string",
  "secondary_muscle_groups": ["string"],
  "exercise_type": "string",
  "equipment": ["string"],
  "difficulty": "string",
  "description": "string",
  "instructions": ["string"],
  "premium_guidance": {
    "form_tips": ["string"],
    "common_mistakes": ["string"],
    "breathing_pattern": "string",
    "progression_tips": ["string"],
    "regression_options": ["string"],
    "safety_notes": ["string"],
    "muscle_activation_cues": ["string"]
  },
  "variations": [
    {
      "name": "string",
      "description": "string",
      "difficulty_modifier": "integer",
      "equipment_changes": ["string"]
    }
  ],
  "met_value": "number",
  "duration_minutes": "integer",
  "tags": ["string"],
  "video_url": "string",
  "image_urls": ["string"],
  "source": "string",
  "verified": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### METValue (Valor MET)

```json
{
  "activity": "string",
  "met_value": "number",
  "exercise_type": "string",
  "intensity": "string",
  "description": "string"
}
```

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Requisição inválida |
| 401 | Não autorizado |
| 404 | Recurso não encontrado |
| 422 | Erro de validação |
| 500 | Erro interno do servidor |

## Autenticação

O Content Service suporta autenticação opcional via Firebase Auth. Para endpoints que requerem autenticação, inclua o token JWT no header:

```
Authorization: Bearer <firebase_jwt_token>
```

### Níveis de Acesso

- **Público**: Dados básicos de alimentos e exercícios
- **Autenticado**: Acesso completo aos dados
- **Premium**: Orientações premium e conteúdo exclusivo

## Rate Limiting

- **Limite**: 100 requisições por minuto por IP
- **Headers de Resposta**:
  - `X-RateLimit-Limit`: Limite total
  - `X-RateLimit-Remaining`: Requisições restantes
  - `X-RateLimit-Reset`: Timestamp do reset

## Caching

O serviço implementa cache em múltiplas camadas:

- **Cache de Aplicação**: TTL de 1 hora para dados estáticos
- **Cache de Query**: Resultados de busca por 15 minutos
- **Cache de Documento**: Documentos individuais por 2 horas

## Monitoramento e Observabilidade

### Métricas Disponíveis

- **Latência**: Tempo de resposta por endpoint
- **Throughput**: Requisições por segundo
- **Taxa de Erro**: Percentual de erros por endpoint
- **Cache Hit Rate**: Taxa de acerto do cache

### Logs Estruturados

Todos os logs seguem formato JSON estruturado:

```json
{
  "timestamp": "2025-08-09T17:30:00Z",
  "level": "INFO",
  "logger": "content_service",
  "message": "Busca de alimentos realizada",
  "search": "frango",
  "filters": {"category": "carnes"},
  "results_count": 5,
  "duration_ms": 45
}
```

## Exemplos de Uso

### Buscar Alimentos Ricos em Proteína

```bash
curl -X GET "https://api.evolveyou.com.br/foods?min_protein=20&max_calories=200&limit=5" \
  -H "Accept: application/json"
```

### Buscar Exercícios para Peito

```bash
curl -X GET "https://api.evolveyou.com.br/exercises?muscle_group=peito&difficulty=intermediario" \
  -H "Accept: application/json"
```

### Calcular Gasto Calórico

```bash
# 1. Obter valor MET
curl -X GET "https://api.evolveyou.com.br/exercises/met-values?exercise_type=forca"

# 2. Calcular: Calorias = MET × peso_kg × tempo_horas
# Exemplo: 3.5 MET × 70kg × 1h = 245 calorias
```

## Integração com API Gateway

### Configuração OpenAPI

O Content Service está integrado ao API Gateway principal da EvolveYou através da especificação OpenAPI. A configuração inclui:

- **Roteamento**: Prefixo `/content` para todos os endpoints
- **Autenticação**: Validação de tokens Firebase
- **Rate Limiting**: Aplicado no nível do gateway
- **CORS**: Configurado para domínios da EvolveYou

### Exemplo de Configuração

```yaml
paths:
  /content/foods:
    get:
      summary: Buscar alimentos
      operationId: searchFoods
      x-google-backend:
        address: https://content-service-url.run.app
        path_translation: APPEND_PATH_TO_ADDRESS
      parameters:
        - name: search
          in: query
          schema:
            type: string
      responses:
        '200':
          description: Lista de alimentos
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FoodSearchResponse'
```

## Deployment

### Variáveis de Ambiente

```bash
# Configurações básicas
ENVIRONMENT=production
PORT=8080
LOG_LEVEL=INFO

# Firebase
FIREBASE_PROJECT_ID=evolveyou-23580
GOOGLE_APPLICATION_CREDENTIALS=/app/serviceAccountKey.json

# Cache
CACHE_TTL=3600
REDIS_URL=redis://redis-service:6379

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Cloud Run

```bash
gcloud run deploy content-service \
  --image gcr.io/evolveyou-prod/content-service \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=evolveyou-23580
```

## Troubleshooting

### Problemas Comuns

#### 1. Erro 500 - Firebase não inicializado

**Causa**: Credenciais do Firebase não configuradas
**Solução**: Verificar variável `GOOGLE_APPLICATION_CREDENTIALS`

#### 2. Erro 422 - Parâmetros inválidos

**Causa**: Parâmetros de query fora dos limites
**Solução**: Verificar documentação dos parâmetros

#### 3. Performance lenta

**Causa**: Cache não configurado ou índices Firestore ausentes
**Solução**: Configurar Redis e criar índices necessários

### Logs de Debug

Para habilitar logs detalhados:

```bash
export LOG_LEVEL=DEBUG
```

## Roadmap

### Versão 1.1

- [ ] Busca por texto completo (Algolia)
- [ ] Recomendações personalizadas
- [ ] Cache distribuído com Redis
- [ ] Métricas avançadas

### Versão 1.2

- [ ] API GraphQL
- [ ] Webhooks para sincronização
- [ ] Versionamento de dados
- [ ] Backup automático

---

**Documentação gerada por:** Manus AI  
**Última atualização:** 09/08/2025  
**Versão da API:** 1.0.0


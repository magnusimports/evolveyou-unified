# 🚪 Gateway Service - API Gateway

## 📋 Visão Geral

O **Gateway Service** é o ponto de entrada único para todas as requisições do EvolveYou. Responsável por roteamento, autenticação, autorização e controle de acesso às funcionalidades premium.

## 🎯 Responsabilidades

### Core Features
- **Roteamento Inteligente**: Direcionamento para microserviços corretos
- **Autenticação Centralizada**: Validação de tokens JWT
- **Rate Limiting**: Proteção contra abuso e spam
- **Load Balancing**: Distribuição de carga entre instâncias

### Security Features
- **Autorização RBAC**: Controle baseado em roles
- **API Key Management**: Gestão de chaves de API
- **Request Validation**: Validação de payloads
- **Security Headers**: Headers de segurança automáticos

### Premium Features
- **Subscription Validation**: Verificação de assinaturas ativas
- **Feature Gating**: Controle de acesso a funcionalidades premium
- **Usage Analytics**: Métricas de uso por usuário
- **Billing Integration**: Integração com sistema de cobrança

## 🏗️ Arquitetura

```
gateway-service/
├── src/
│   ├── server.js            # Ponto de entrada
│   ├── config/              # Configurações
│   ├── middleware/          # Middleware
│   │   ├── auth.js              # Autenticação
│   │   ├── rateLimit.js         # Rate limiting
│   │   ├── validation.js        # Validação
│   │   └── premium.js           # Controle premium
│   ├── routes/              # Roteamento
│   │   ├── proxy.js             # Proxy para serviços
│   │   ├── auth.js              # Rotas de auth
│   │   └── health.js            # Health checks
│   ├── services/            # Lógica de negócio
│   │   ├── routingService.js    # Roteamento
│   │   ├── authService.js       # Autenticação
│   │   └── premiumService.js    # Premium
│   └── utils/               # Utilitários
├── tests/                   # Testes
├── package.json            # Dependências
├── Dockerfile              # Container
└── README.md               # Documentação
```

## 🔗 Funcionalidades Principais

### Roteamento
```javascript
// Exemplo de configuração de rotas
const routes = {
  '/api/users/*': 'users-service',
  '/api/plans/*': 'plans-service',
  '/api/content/*': 'content-service',
  '/api/tracking/*': 'tracking-service',
  '/api/evo/*': 'evo-service'
};
```

### Autenticação
```javascript
// Middleware de autenticação
const authMiddleware = async (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Token required' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};
```

### Rate Limiting
```javascript
// Configuração de rate limiting
const rateLimitConfig = {
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // máximo 100 requests por janela
  premium: {
    max: 1000 // usuários premium têm limite maior
  }
};
```

### Controle Premium
```javascript
// Middleware de controle premium
const premiumMiddleware = async (req, res, next) => {
  const user = req.user;
  const endpoint = req.path;
  
  if (isPremiumEndpoint(endpoint) && !user.isPremium) {
    return res.status(403).json({ 
      error: 'Premium subscription required',
      upgradeUrl: '/premium/upgrade'
    });
  }
  
  next();
};
```

## 🔐 Segurança

### Headers de Segurança
```javascript
// Headers automáticos
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000');
  next();
});
```

### Validação de Requests
```javascript
// Validação de payload
const validateRequest = (schema) => {
  return (req, res, next) => {
    const { error } = schema.validate(req.body);
    if (error) {
      return res.status(400).json({ 
        error: 'Invalid request',
        details: error.details 
      });
    }
    next();
  };
};
```

## 📊 Monitoramento e Logs

### Métricas Coletadas
- Número de requests por endpoint
- Tempo de resposta por serviço
- Taxa de erro por microserviço
- Uso por usuário premium vs gratuito

### Logs Estruturados
```javascript
// Formato de log
{
  "timestamp": "2025-08-16T10:30:00Z",
  "level": "info",
  "method": "GET",
  "path": "/api/plans/diet",
  "userId": "user_123",
  "responseTime": 245,
  "statusCode": 200,
  "service": "plans-service"
}
```

## 🚀 Configuração de Serviços

### Service Discovery
```javascript
// Configuração de serviços
const services = {
  'users-service': {
    url: process.env.USERS_SERVICE_URL,
    healthCheck: '/health',
    timeout: 5000
  },
  'plans-service': {
    url: process.env.PLANS_SERVICE_URL,
    healthCheck: '/health',
    timeout: 10000
  },
  'evo-service': {
    url: process.env.EVO_SERVICE_URL,
    healthCheck: '/health',
    timeout: 15000
  }
};
```

### Circuit Breaker
```javascript
// Proteção contra falhas
const circuitBreaker = new CircuitBreaker(callService, {
  timeout: 3000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000
});
```

## 🔄 Funcionalidades Premium

### Endpoints Premium
```javascript
const premiumEndpoints = [
  '/api/evo/guided-workout',
  '/api/evo/analyze-photo',
  '/api/plans/premium-features',
  '/api/tracking/advanced-analytics'
];
```

### Validação de Assinatura
```javascript
const validateSubscription = async (userId) => {
  const subscription = await getSubscription(userId);
  
  return {
    isActive: subscription.status === 'active',
    plan: subscription.plan,
    expiresAt: subscription.expiresAt,
    features: subscription.features
  };
};
```

## 📈 Performance

### Caching
```javascript
// Cache de responses
const cache = new NodeCache({ stdTTL: 300 }); // 5 minutos

app.use('/api/content', (req, res, next) => {
  const key = req.originalUrl;
  const cached = cache.get(key);
  
  if (cached) {
    return res.json(cached);
  }
  
  next();
});
```

### Compression
```javascript
// Compressão de responses
app.use(compression({
  filter: (req, res) => {
    return compression.filter(req, res);
  },
  threshold: 1024
}));
```

## 🧪 Testes

### Tipos de Teste
- **Unit Tests**: Middleware e utilitários
- **Integration Tests**: Roteamento e proxy
- **Load Tests**: Performance sob carga
- **Security Tests**: Vulnerabilidades

### Cobertura
- Mínimo 90% de cobertura
- Testes de segurança obrigatórios
- Testes de performance regulares
- Validação de rate limiting

## 🔄 Roadmap

### Fase 1 (Semana 1)
- [ ] Estrutura básica do gateway
- [ ] Roteamento para serviços existentes
- [ ] Autenticação JWT
- [ ] Rate limiting básico

### Fase 2 (Semana 2)
- [ ] Controle de acesso premium
- [ ] Validação de requests
- [ ] Headers de segurança
- [ ] Monitoramento básico

### Fase 3 (Semana 3)
- [ ] Circuit breaker
- [ ] Caching inteligente
- [ ] Analytics avançados
- [ ] Otimização de performance

### Fase 4 (Semana 4)
- [ ] Testes de carga
- [ ] Monitoramento avançado
- [ ] Alertas automáticos
- [ ] Deploy em produção

## 📊 Métricas de Sucesso

### Performance
- Latência < 50ms para roteamento
- Throughput > 1000 req/s
- Disponibilidade > 99.9%
- Tempo de resposta < 100ms

### Segurança
- Zero vulnerabilidades críticas
- Rate limiting efetivo
- Autenticação 100% funcional
- Logs de auditoria completos

---

**O Gateway Service é a porta de entrada segura e inteligente que protege e otimiza todo o ecossistema EvolveYou.**


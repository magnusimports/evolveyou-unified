# 📋 EVOLVEYOU - DOCUMENTO MASTER DO PROJETO

## 🎯 VISÃO GERAL DO PROJETO

**EvolveYou** é um aplicativo revolucionário de fitness e nutrição que oferece planos personalizados com sistema **Full-time** (rebalanceamento automático de calorias) e renovação automática a cada 45 dias.

### **Diferencial Competitivo**
- **Sistema Full-time**: Rebalanceamento automático quando usuário faz atividades extras
- **Ciclos de 45 dias**: Renovação automática de planos
- **Algoritmos avançados**: Geração inteligente de dietas e treinos
- **Base brasileira**: Tabela TACO com 3000+ alimentos nacionais

---

## 📊 STATUS ATUAL DO PROJETO (14/08/2025)

### **🏗️ BACKEND: 75% COMPLETO**
- ✅ **Plans-Service**: 90% - Algoritmos avançados implementados
- ✅ **Users-Service**: 85% - Autenticação + onboarding completos
- ✅ **Tracking-Service**: 70% - Estrutura avançada com rotas especializadas
- ✅ **Content-Service**: 40% - Estrutura sólida, falta popular dados
- ✅ **Health-Check-Service**: 100% - Monitoramento completo
- ✅ **Infraestrutura**: 95% - CI/CD, Docker, Terraform configurados

### **📱 FRONTEND: 60% COMPLETO**
- ✅ **11 telas implementadas** com navegação completa
- ✅ **Firebase configurado**
- ✅ **Widgets customizados** profissionais
- ✅ **Autenticação** com Provider
- ✅ **Tema** light/dark implementado

### **⏱️ ESTIMATIVA DE CONCLUSÃO: 20-25 DIAS**

---

## 🗂️ ESTRUTURA DOS REPOSITÓRIOS

### **📁 evolveyou-backend**
```
evolveyou-backend/
├── services/
│   ├── content-service/          # Alimentos e exercícios
│   ├── users-service/            # Usuários e autenticação
│   ├── plans-service/            # Geração de planos
│   ├── tracking-service/         # Acompanhamento
│   └── health-check-service/     # Monitoramento
├── infrastructure/               # Terraform
├── docs/                        # Documentação
└── tools/                       # Scripts utilitários
```

### **📁 evolveyou-frontend**
```
evolveyou-frontend/
├── lib/
│   ├── screens/                 # 11 telas implementadas
│   ├── services/                # Serviços de API
│   ├── widgets/                 # Componentes customizados
│   ├── constants/               # Constantes e temas
│   └── models/                  # Modelos de dados
├── assets/                      # Recursos visuais
└── android/ios/web/            # Configurações de plataforma
```

---

## 🔧 TECNOLOGIAS E FERRAMENTAS

### **Backend**
- **Runtime**: Google Cloud Run
- **Database**: Google Firestore
- **Languages**: Python (FastAPI), Node.js
- **Auth**: JWT + Firebase Auth
- **CI/CD**: GitHub Actions + Cloud Build
- **Monitoring**: Cloud Monitoring + Logging

### **Frontend**
- **Framework**: Flutter (Dart)
- **State Management**: Provider
- **Auth**: Firebase Auth
- **Navigation**: Named Routes
- **UI**: Material Design + Custom Theme

### **Infraestrutura**
- **Cloud**: Google Cloud Platform
- **Project ID**: `evolveyou-prod`
- **Containers**: Docker + Cloud Run
- **IaC**: Terraform
- **Registry**: Artifact Registry

---

## 🎯 FUNCIONALIDADES IMPLEMENTADAS

### ✅ **BACKEND IMPLEMENTADO**

#### **1. Plans-Service (90% COMPLETO)**
**Localização**: `evolveyou-backend/services/plans-service/`

**APIs Disponíveis**:
```
GET  /plan/diet              - Plano de dieta personalizado
GET  /plan/workout           - Plano de treino personalizado  
GET  /plan/presentation      - Apresentação do plano
GET  /plan/weekly-schedule   - Cronograma semanal
POST /admin/regenerate-plans - Regenerar planos (admin)
```

**Algoritmos Implementados**:
- ✅ **Geração de dieta**: Cálculo calórico, distribuição de macros, seleção inteligente
- ✅ **Geração de treino**: Seleção de exercícios, progressão, periodização
- ✅ **Otimização de quantidades**: Algoritmo matemático avançado
- ✅ **Sistema de scoring**: Adequação nutricional e preferências

**Arquivos Principais**:
- `src/main.py` - API principal
- `src/algorithms/diet_generator.py` - Algoritmo de dieta (EXCEPCIONAL)
- `src/algorithms/workout_generator.py` - Algoritmo de treino
- `src/services/plan_service.py` - Lógica de negócio

#### **2. Users-Service (85% COMPLETO)**
**Localização**: `evolveyou-backend/services/users-service/`

**APIs Disponíveis**:
```
POST /auth/register          - Registro de usuário
POST /auth/login             - Login email/senha
POST /auth/social-login      - Login social (Google, Apple, Facebook)
POST /auth/refresh           - Renovar token
GET  /users/me               - Perfil atual
POST /onboarding/submit      - Submeter onboarding
POST /calories/recalculate   - Recalcular calorias
```

**Funcionalidades**:
- ✅ **Autenticação JWT** completa
- ✅ **Login social** (Google, Apple, Facebook)
- ✅ **Onboarding** com questionário completo
- ✅ **Cálculo calórico** automático
- ✅ **Rate limiting** avançado

#### **3. Tracking-Service (70% COMPLETO)**
**Localização**: `evolveyou-backend/services/tracking-service/`

**Estrutura**:
- ✅ **logging_routes** - Registro de atividades
- ✅ **dashboard_routes** - Dashboard de progresso
- ✅ **progress_routes** - Acompanhamento de metas
- ✅ **Cache service** implementado

#### **4. Content-Service (40% COMPLETO)**
**Localização**: `evolveyou-backend/services/content-service/`

**APIs Disponíveis**:
```
GET /api/foods               - Lista de alimentos
GET /api/foods/{id}          - Detalhes do alimento
GET /api/exercises           - Lista de exercícios
GET /api/categories/exercises - Categorias de exercícios
```

**Status**: Estrutura completa, mas apenas 3 alimentos/exercícios de exemplo

### ✅ **FRONTEND IMPLEMENTADO**

#### **Telas Desenvolvidas**:
1. ✅ **SplashScreen** - Carregamento inicial
2. ✅ **WelcomeScreen** - Boas-vindas
3. ✅ **LoginScreen** - Login com validação
4. ✅ **RegisterScreen** - Registro de usuário
5. ✅ **OnboardingScreen** - Questionário inicial
6. ✅ **MainNavigationScreen** - Navegação principal
7. ✅ **DashboardScreen** - Dashboard principal
8. ✅ **ProgressScreen** - Acompanhamento
9. ✅ **NutritionScreen** - Nutrição
10. ✅ **WorkoutScreen** - Treinos
11. ✅ **ProfileScreen** - Perfil

#### **Componentes Customizados**:
- ✅ `CustomButton` - Botões padronizados
- ✅ `CustomTextField` - Campos de texto
- ✅ `LoadingOverlay` - Overlay de carregamento
- ✅ `EvoAvatarWidget` - Avatar personalizado

---

## ❌ FUNCIONALIDADES FALTANTES (CRÍTICAS)

### **🔥 PRIORIDADE MÁXIMA**

#### **1. BASE DE DADOS COMPLETA (5% IMPLEMENTADO)**
**Problema**: Apenas 3 alimentos e 3 exercícios de exemplo
**Solução**: Popular com tabela TACO brasileira (3000+ alimentos)

**Localização**: `evolveyou-backend/services/content-service/`
**Arquivos**: 
- `scripts/populate_database.py` (existe, mas incompleto)
- `scripts/populate_firestore_massive.py` (existe)

**Tarefas**:
1. Baixar tabela TACO oficial brasileira
2. Processar dados nutricionais
3. Categorizar alimentos
4. Popular Firestore
5. Criar base de exercícios completa

#### **2. SISTEMA FULL-TIME (0% IMPLEMENTADO)**
**Descrição**: Funcionalidade principal - rebalanceamento automático
**Localização**: `evolveyou-backend/services/tracking-service/`

**Componentes Necessários**:
1. **Registro de atividades extras**
2. **Registro de alimentos não planejados**
3. **Algoritmo de rebalanceamento calórico**
4. **Redistribuição automática nos próximos dias**
5. **Validações de segurança (BMR)**

**Arquivos a Criar**:
- `src/algorithms/rebalancing_algorithm.py`
- `src/services/fulltime_service.py`
- `src/routes/fulltime_routes.py`

#### **3. SISTEMA DE CICLOS (0% IMPLEMENTADO)**
**Descrição**: Renovação automática a cada 45 dias
**Tecnologias**: Cloud Functions + Cloud Scheduler

**Componentes Necessários**:
1. **Cloud Function** para verificar ciclos expirados
2. **Cloud Scheduler** para execução diária
3. **Notificações** de fim de ciclo
4. **Regeneração automática** de planos

**Arquivos a Criar**:
- `cloud-functions/cycle-renewal/main.py`
- `infrastructure/terraform/scheduler.tf`

#### **4. INTEGRAÇÃO FRONTEND-BACKEND (0% IMPLEMENTADO)**
**Problema**: APIs não conectadas ao app Flutter
**Localização**: `evolveyou-frontend/lib/services/`

**Tarefas**:
1. Implementar chamadas HTTP para todas as APIs
2. Configurar autenticação JWT no Flutter
3. Implementar estado global (Provider/Riverpod)
4. Adicionar cache local
5. Tratamento de erros

### **⚡ ALTA PRIORIDADE**

#### **5. TELAS DE ANAMNESE DETALHADAS (20% IMPLEMENTADO)**
**Problema**: OnboardingScreen existe mas é básica
**Localização**: `evolveyou-frontend/lib/screens/`

**Telas a Criar**:
1. `anamnese/objectives_screen.dart`
2. `anamnese/body_data_screen.dart`
3. `anamnese/food_preferences_screen.dart`
4. `anamnese/restrictions_screen.dart`
5. `anamnese/activity_level_screen.dart`
6. `anamnese/summary_screen.dart`

#### **6. SISTEMA DE EQUIVALÊNCIA (0% IMPLEMENTADO)**
**Descrição**: Substituição inteligente de alimentos
**Localização**: Novo microserviço

**Componentes**:
1. **Algoritmo de equivalência nutricional**
2. **API de substituições**
3. **Interface no frontend**

#### **7. LISTA DE COMPRAS (0% IMPLEMENTADO)**
**Descrição**: Geração automática de listas
**Localização**: Novo microserviço ou extensão do plans-service

**Funcionalidades**:
1. **Geração automática** baseada nos planos
2. **Agregação por período**
3. **Interface de marcação**
4. **Otimização de compras** (premium)

### **💎 FUNCIONALIDADES PREMIUM**

#### **8. INTEGRAÇÃO COM IA (0% IMPLEMENTADO)**
**Tecnologia**: Google Vertex AI
**Funcionalidades**:
1. **Análise de imagens corporais**
2. **Coach motivacional**
3. **Chatbot para dúvidas**

#### **9. SISTEMA DE PAGAMENTOS (0% IMPLEMENTADO)**
**Tecnologia**: Stripe
**Funcionalidades**:
1. **Planos de assinatura**
2. **Controle de acesso premium**
3. **Webhooks de pagamento**

---

## 🚀 PLANO DE IMPLEMENTAÇÃO DETALHADO

### **📅 CRONOGRAMA OTIMIZADO (20-25 DIAS)**

#### **SEMANA 1 (Dias 1-5): FUNDAÇÃO**

**Dia 1-2: Base de Dados TACO**
- [ ] Baixar tabela TACO oficial brasileira
- [ ] Processar dados nutricionais (calorias, macros, micros)
- [ ] Categorizar alimentos por grupos
- [ ] Criar script de população do Firestore
- [ ] Popular 3000+ alimentos brasileiros

**Arquivos a Modificar**:
```
evolveyou-backend/services/content-service/
├── scripts/populate_taco_database.py (criar)
├── data/taco_brasileira.csv (baixar)
└── src/services/content_service.py (atualizar)
```

**Dia 3-4: Telas de Anamnese**
- [ ] Criar fluxo de anamnese detalhado
- [ ] Implementar 6 telas específicas
- [ ] Validação de dados
- [ ] Navegação entre telas
- [ ] Integração com backend

**Arquivos a Criar**:
```
evolveyou-frontend/lib/screens/anamnese/
├── anamnese_flow.dart
├── objectives_screen.dart
├── body_data_screen.dart
├── food_preferences_screen.dart
├── restrictions_screen.dart
├── activity_level_screen.dart
└── summary_screen.dart
```

**Dia 5: Integração Frontend-Backend**
- [ ] Implementar AuthService completo
- [ ] Configurar chamadas HTTP
- [ ] Testar autenticação JWT
- [ ] Configurar estado global

#### **SEMANA 2 (Dias 6-10): FUNCIONALIDADES CORE**

**Dia 6-7: Sistema de Ciclos**
- [ ] Criar Cloud Function para renovação
- [ ] Configurar Cloud Scheduler
- [ ] Implementar notificações push
- [ ] Testar renovação automática

**Arquivos a Criar**:
```
cloud-functions/
├── cycle-renewal/
│   ├── main.py
│   ├── requirements.txt
│   └── deploy.sh
└── infrastructure/terraform/
    └── scheduler.tf
```

**Dia 8-9: Sistema de Equivalência**
- [ ] Criar algoritmo de equivalência nutricional
- [ ] Implementar API de substituições
- [ ] Criar interface no frontend
- [ ] Testar substituições

**Dia 10: Lista de Compras Básica**
- [ ] Implementar geração automática
- [ ] Criar interface de marcação
- [ ] Integrar com planos existentes

#### **SEMANA 3 (Dias 11-15): SISTEMA FULL-TIME**

**Dia 11-12: Tracking de Atividades Extras**
- [ ] Implementar registro de atividades não planejadas
- [ ] Criar interface de tracking
- [ ] Calcular calorias queimadas extras

**Dia 13-14: Algoritmo de Rebalanceamento**
- [ ] Implementar algoritmo de redistribuição calórica
- [ ] Validações de segurança (BMR)
- [ ] Distribuição nos próximos 5 dias
- [ ] Logs e auditoria

**Arquivos a Criar**:
```
evolveyou-backend/services/tracking-service/src/
├── algorithms/
│   └── rebalancing_algorithm.py
├── services/
│   └── fulltime_service.py
└── routes/
    └── fulltime_routes.py
```

**Dia 15: Interface de Tracking Dinâmico**
- [ ] Tela de registro de atividades extras
- [ ] Dashboard de balanço calórico
- [ ] Notificações de rebalanceamento
- [ ] Histórico de ajustes

#### **SEMANA 4 (Dias 16-20): PREMIUM E POLIMENTO**

**Dia 16-17: Funcionalidades Premium**
- [ ] Integração com Vertex AI
- [ ] Análise de imagens corporais
- [ ] Coach motivacional

**Dia 18-19: Sistema de Pagamentos**
- [ ] Integração com Stripe
- [ ] Planos de assinatura
- [ ] Controle de acesso

**Dia 20: Testes e Otimizações**
- [ ] Testes de integração
- [ ] Otimização de performance
- [ ] Correção de bugs

#### **SEMANA 5 (Dias 21-25): FINALIZAÇÃO**

**Dia 21-23: Testes Finais**
- [ ] Testes end-to-end
- [ ] Testes de carga
- [ ] Validação de segurança

**Dia 24-25: Deploy e Documentação**
- [ ] Deploy em produção
- [ ] Documentação final
- [ ] Treinamento do usuário

---

## 🔑 CREDENCIAIS E ACESSOS

### **Google Cloud Platform**
- **Project ID**: `evolveyou-prod`
- **Console**: https://console.cloud.google.com/welcome?project=evolveyou-prod
- **Status**: ✅ Configurado

### **Firebase**
- **Console**: https://console.firebase.google.com/u/0/?hl=pt-br
- **Status**: ✅ Configurado

### **GitHub**
- **Backend**: https://github.com/magnusimports/evolveyou-backend
- **Frontend**: https://github.com/magnusimports/evolveyou-frontend
- **Token**: `YOUR_GITHUB_TOKEN`
- **Status**: ✅ Repositórios clonados

### **APIs Necessárias**
- [ ] Google Maps Platform (lista de compras)
- [ ] Vertex AI (funcionalidades premium)
- [ ] Stripe (pagamentos)
- [ ] Firebase Cloud Messaging (notificações)

---

## 📝 COMANDOS ÚTEIS

### **Desenvolvimento Local**
```bash
# Backend
cd evolveyou-backend
docker-compose up -d

# Frontend
cd evolveyou-frontend
flutter run

# Testes
cd evolveyou-backend
python -m pytest

# Deploy
gcloud builds submit --config cloudbuild.yaml
```

### **Firestore**
```bash
# Popular dados
python evolveyou-backend/services/content-service/scripts/populate_database.py

# Backup
gcloud firestore export gs://evolveyou-prod-backup
```

---

## 🚨 PONTOS CRÍTICOS DE ATENÇÃO

### **1. Algoritmo de Rebalanceamento**
- **CRÍTICO**: Validar BMR para evitar déficits perigosos
- **Limite mínimo**: Nunca reduzir abaixo do BMR
- **Distribuição**: Máximo 5 dias para redistribuir excesso
- **Logging**: Registrar todos os rebalanceamentos

### **2. Segurança**
- **Autenticação**: JWT com refresh tokens
- **Rate limiting**: Implementado em todos os serviços
- **Validação**: Sanitizar todas as entradas
- **HTTPS**: Obrigatório em produção

### **3. Performance**
- **Cache**: Redis para consultas frequentes
- **CDN**: Para assets estáticos
- **Lazy loading**: No frontend
- **Pagination**: Para listas grandes

### **4. Monitoramento**
- **Health checks**: Implementados
- **Logs estruturados**: Configurados
- **Alertas**: Configurar para falhas críticas
- **Métricas**: Dashboards no Cloud Monitoring

---

## 🎯 CRITÉRIOS DE SUCESSO

### **MVP (Minimum Viable Product)**
- [ ] Usuário pode se registrar e fazer login
- [ ] Onboarding completo funcional
- [ ] Geração de planos de dieta e treino
- [ ] Base de dados TACO completa
- [ ] Sistema full-time básico

### **Produto Completo**
- [ ] Todas as funcionalidades implementadas
- [ ] Sistema de ciclos automático
- [ ] Funcionalidades premium
- [ ] Sistema de pagamentos
- [ ] Testes completos e deploy em produção

---

## 📞 PRÓXIMOS PASSOS IMEDIATOS

### **Para o Próximo Agente**

1. **Verificar Status**:
   - [ ] Repositórios atualizados
   - [ ] Credenciais funcionando
   - [ ] Ambiente de desenvolvimento configurado

2. **Começar Implementação**:
   - [ ] Prioridade 1: Base de dados TACO
   - [ ] Prioridade 2: Telas de anamnese
   - [ ] Prioridade 3: Integração frontend-backend

3. **Validar Progresso**:
   - [ ] Testar cada funcionalidade implementada
   - [ ] Atualizar este documento com progresso
   - [ ] Comunicar bloqueios ou mudanças

### **Comandos para Começar**
```bash
# Clonar repositórios (se necessário)
git clone https://github.com/magnusimports/evolveyou-backend.git
git clone https://github.com/magnusimports/evolveyou-frontend.git

# Configurar ambiente
cd evolveyou-backend
docker-compose up -d

# Verificar status dos serviços
curl http://localhost:8080/health  # content-service
curl http://localhost:8081/health  # users-service
curl http://localhost:8082/health  # plans-service
```

---

## 📚 RECURSOS ADICIONAIS

### **Documentação Técnica**
- **FastAPI**: https://fastapi.tiangolo.com/
- **Flutter**: https://flutter.dev/docs
- **Firebase**: https://firebase.google.com/docs
- **Google Cloud**: https://cloud.google.com/docs

### **Tabela TACO**
- **Oficial**: https://www.tbca.net.br/
- **IBGE**: https://biblioteca.ibge.gov.br/
- **Dataset Kaggle**: https://www.kaggle.com/datasets/eriannefarias/brazilian-food-composition-table-tbca

### **APIs Úteis**
- **Nutrition**: https://api.nal.usda.gov/fdc/v1/
- **Exercise**: https://wger.de/en/software/api
- **Maps**: https://developers.google.com/maps

---

## ✅ CHECKLIST DE CONTINUIDADE

### **Antes de Começar**
- [ ] Documento lido e compreendido
- [ ] Repositórios clonados e atualizados
- [ ] Ambiente de desenvolvimento configurado
- [ ] Credenciais testadas e funcionando

### **Durante o Desenvolvimento**
- [ ] Seguir cronograma proposto
- [ ] Testar cada funcionalidade implementada
- [ ] Atualizar documentação com progresso
- [ ] Fazer commits frequentes com mensagens claras

### **Ao Finalizar**
- [ ] Todos os testes passando
- [ ] Documentação atualizada
- [ ] Deploy realizado com sucesso
- [ ] Usuário final validou funcionalidades

---

**📅 Documento criado em: 14/08/2025**
**👤 Criado por: Agente Manus**
**🔄 Última atualização: 14/08/2025**
**📋 Status: PRONTO PARA CONTINUIDADE**

---

*Este documento serve como guia completo para qualquer agente que assumir o projeto EvolveYou. Mantenha-o atualizado conforme o progresso da implementação.*


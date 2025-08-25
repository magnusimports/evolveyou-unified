# Regras de Segurança Firestore - Content Service

## Visão Geral

Este documento descreve as regras de segurança implementadas no Firestore para o Content Service da EvolveYou. As regras garantem que apenas usuários autorizados possam acessar e modificar dados específicos.

## Estrutura de Permissões

### Níveis de Acesso

1. **Público**: Qualquer pessoa pode acessar
2. **Autenticado**: Apenas usuários logados
3. **Proprietário**: Apenas o dono dos dados
4. **Premium**: Apenas usuários com plano premium/pro
5. **Admin**: Apenas administradores

### Coleções e Permissões

#### 🍎 Foods (Alimentos)
- **Leitura**: Pública (todos podem ver alimentos)
- **Escrita**: Apenas admins
- **Validação**: Nome, categoria e informações nutricionais obrigatórias

```javascript
// Exemplo de acesso
// ✅ Permitido: GET /foods
// ❌ Negado: POST /foods (sem ser admin)
```

#### 💪 Exercises (Exercícios)
- **Leitura Básica**: Pública
- **Leitura Premium**: Apenas usuários premium podem ver `premium_guidance`
- **Escrita**: Apenas admins
- **Validação**: Nome, grupo muscular, tipo, equipamento obrigatórios

```javascript
// Exemplo de acesso
// ✅ Permitido: GET /exercises (dados básicos)
// ✅ Permitido: GET /exercises (premium_guidance) - se for premium
// ❌ Negado: GET /exercises (premium_guidance) - se for gratuito
```

#### ⚡ MET Values
- **Leitura**: Pública
- **Escrita**: Apenas admins
- **Validação**: Atividade, valor MET e tipo obrigatórios

#### 👤 Users (Usuários)
- **Leitura**: Próprio usuário ou admin
- **Escrita**: Próprio usuário ou admin
- **Validação**: Email e nome obrigatórios, email válido

#### 🏋️ Workouts (Treinos)
- **Leitura**: Apenas o dono do treino ou admin
- **Escrita**: Apenas o dono do treino ou admin
- **Validação**: userId deve corresponder ao usuário autenticado

#### 🥗 Nutrition (Nutrição)
- **Leitura**: Apenas o dono dos dados ou admin
- **Escrita**: Apenas o dono dos dados ou admin
- **Validação**: userId deve corresponder ao usuário autenticado

## Funções de Validação

### validateFoodData()
Valida dados de alimentos:
- Nome (string)
- Categoria (string)
- Informações nutricionais (objeto com calorias, proteína, carboidratos, gordura)

### validateExerciseData()
Valida dados de exercícios:
- Nome (string)
- Grupo muscular principal (string)
- Tipo de exercício (string)
- Equipamentos (array)
- Dificuldade (string)
- Descrição (string)
- Instruções (array)

### validateMETData()
Valida valores MET:
- Atividade (string)
- Valor MET (número > 0)
- Tipo de exercício (string)

### validateUserData()
Valida dados de usuário:
- Email (string válido)
- Nome (string)

### validateWorkoutData()
Valida dados de treino:
- userId deve corresponder ao usuário autenticado
- Nome (string)
- Exercícios (array)

### validateNutritionData()
Valida dados nutricionais:
- userId deve corresponder ao usuário autenticado
- Data (timestamp)
- Refeições (array)

## Implementação das Regras

### 1. Deploy das Regras

```bash
# Instalar Firebase CLI
npm install -g firebase-tools

# Login no Firebase
firebase login

# Configurar projeto
firebase use evolveyou-23580

# Deploy das regras
firebase deploy --only firestore:rules
```

### 2. Teste das Regras

```bash
# Executar emulador para testes
firebase emulators:start --only firestore

# Executar testes de regras
firebase emulators:exec --only firestore "npm test"
```

### 3. Monitoramento

As regras incluem logging automático para:
- Tentativas de acesso negado
- Validações que falharam
- Acessos a dados premium

## Cenários de Uso

### Usuário Gratuito
```javascript
// ✅ Pode ver alimentos
GET /foods

// ✅ Pode ver exercícios básicos
GET /exercises

// ❌ Não pode ver orientações premium
GET /exercises/{id} // premium_guidance será filtrado

// ✅ Pode ver seus próprios treinos
GET /workouts?userId=own_id

// ❌ Não pode ver treinos de outros
GET /workouts?userId=other_id
```

### Usuário Premium
```javascript
// ✅ Pode ver alimentos
GET /foods

// ✅ Pode ver exercícios completos
GET /exercises // incluindo premium_guidance

// ✅ Pode ver valores MET
GET /exercises/met-values

// ✅ Pode gerenciar seus dados
POST /workouts
PUT /nutrition/{id}
```

### Administrador
```javascript
// ✅ Pode fazer tudo
POST /foods
PUT /exercises/{id}
DELETE /foods/{id}

// ✅ Pode ver dados de qualquer usuário
GET /users/{any_id}
GET /workouts?userId=any_id
```

## Segurança Adicional

### Rate Limiting
- Implementado no nível da aplicação
- 100 requests por minuto por IP

### Validação de Entrada
- Todos os dados são validados no backend
- Sanitização de strings
- Validação de tipos

### Auditoria
- Logs estruturados de todas as operações
- Monitoramento de tentativas de acesso negado
- Alertas para atividades suspeitas

## Manutenção

### Atualização de Regras
1. Modificar arquivo `firestore.rules`
2. Testar em ambiente de desenvolvimento
3. Deploy para produção
4. Monitorar logs por 24h

### Backup de Regras
- Regras são versionadas no Git
- Backup automático no Firebase Console
- Histórico de mudanças mantido

## Troubleshooting

### Erro: "Permission denied"
1. Verificar se usuário está autenticado
2. Verificar se tem permissão para a operação
3. Verificar se dados passam na validação

### Erro: "Invalid data"
1. Verificar estrutura dos dados
2. Verificar tipos de campos
3. Verificar campos obrigatórios

### Performance
- Regras são avaliadas em ordem
- Usar índices para queries complexas
- Monitorar tempo de resposta das regras


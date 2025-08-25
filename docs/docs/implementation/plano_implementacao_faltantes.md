# Plano de Implementação - Funcionalidades Faltantes

## 🎯 SITUAÇÃO ATUAL: PROJETO 40% COMPLETO

**EXCELENTE NOTÍCIA**: O projeto já possui uma **base sólida** com arquitetura profissional e algoritmos avançados implementados!

**NOVA ESTIMATIVA**: **30-40 dias** para completar (ao invés de 60 dias)

## 📋 Prioridades de Implementação

### **🔥 CRÍTICO - Semana 1-2**

#### 1. **Base de Dados Completa**
```python
# Implementar população da tabela TACO brasileira
- 3.000+ alimentos brasileiros
- Informações nutricionais completas
- Categorização adequada
- Sistema de busca otimizado
```

#### 2. **Sistema de Anamnese (Frontend)**
```dart
// Telas de questionário no Flutter
- Tela de objetivos
- Tela de dados corporais
- Tela de preferências alimentares
- Tela de restrições
- Tela de nível de atividade
```

#### 3. **Integração Frontend-Backend**
```dart
// Conectar APIs existentes
- Autenticação JWT
- Chamadas para geração de planos
- Estado global com Provider/Riverpod
- Cache local de dados
```

### **⚡ ALTA PRIORIDADE - Semana 3-4**

#### 4. **Sistema de Ciclos de 45 Dias**
```python
# Cloud Functions + Scheduler
- Função de renovação automática
- Agendamento diário de verificação
- Notificações de fim de ciclo
- Histórico de ciclos
```

#### 5. **Serviço de Equivalência Nutricional**
```python
# Novo microserviço: equivalence-service
- Algoritmo de substituição
- Cálculo de equivalência calórica
- API REST para substituições
- Interface no frontend
```

#### 6. **Lista de Compras Inteligente**
```python
# Novo microserviço: shopping-service
- Geração automática de listas
- Agregação por período
- Interface de marcação no frontend
```

### **🚀 FUNCIONALIDADE PRINCIPAL - Semana 5-6**

#### 7. **Sistema Full-time (DIFERENCIAL COMPETITIVO)**
```python
# Expansão do tracking-service
- Registro de atividades extras
- Registro de alimentos não planejados
- Algoritmo de rebalanceamento
- Redistribuição inteligente de calorias
- Validações de segurança (BMR)
```

#### 8. **Interface de Tracking Dinâmico**
```dart
// Frontend para sistema full-time
- Tela de registro de atividades
- Tela de registro de alimentos extras
- Dashboard de balanço calórico
- Notificações de rebalanceamento
```

### **💎 PREMIUM - Semana 7-8**

#### 9. **Funcionalidades Premium**
```python
# ai-service com Vertex AI
- Análise de imagens corporais
- Coach motivacional
- Chatbot para dúvidas
```

#### 10. **Sistema de Pagamentos**
```python
# payment-service com Stripe
- Planos de assinatura
- Controle de acesso premium
- Webhooks de pagamento
```

## 🛠️ Implementação Detalhada

### **1. Base de Dados TACO (Prioridade 1)**

```python
# Script para popular Firestore
import pandas as pd
from firebase_admin import firestore

def populate_taco_database():
    # Carregar tabela TACO oficial
    taco_data = pd.read_csv('taco_brasileira.csv')
    
    db = firestore.client()
    foods_ref = db.collection('foods')
    
    for _, food in taco_data.iterrows():
        food_doc = {
            'name': food['nome'],
            'category': food['categoria'],
            'nutrition': {
                'calories': food['energia_kcal'],
                'protein': food['proteina_g'],
                'carbs': food['carboidrato_g'],
                'fat': food['lipidio_g'],
                'fiber': food['fibra_g'],
                'sodium': food['sodio_mg']
            },
            'preparation_time': estimate_prep_time(food['categoria']),
            'cost_level': estimate_cost_level(food['nome']),
            'availability_score': 0.8,
            'dietary_tags': generate_dietary_tags(food),
            'allergens': identify_allergens(food)
        }
        
        foods_ref.add(food_doc)
```

### **2. Sistema de Anamnese (Flutter)**

```dart
// anamnese_flow.dart
class AnamneseFlow extends StatefulWidget {
  @override
  _AnamneseFlowState createState() => _AnamneseFlowState();
}

class _AnamneseFlowState extends State<AnamneseFlow> {
  PageController _pageController = PageController();
  AnamneseData _data = AnamneseData();
  
  List<Widget> _pages = [
    ObjectivesScreen(),
    BodyDataScreen(),
    FoodPreferencesScreen(),
    RestrictionsScreen(),
    ActivityLevelScreen(),
    SummaryScreen(),
  ];
  
  void _nextPage() {
    _pageController.nextPage(
      duration: Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }
  
  void _submitAnamnese() async {
    try {
      await UserService.submitAnamnese(_data);
      Navigator.pushReplacementNamed(context, '/dashboard');
    } catch (e) {
      // Handle error
    }
  }
}
```

### **3. Sistema de Ciclos (Cloud Functions)**

```python
# cloud_function_cycles.py
import functions_framework
from google.cloud import firestore
from datetime import datetime, timedelta

@functions_framework.http
def check_expired_cycles(request):
    """Verifica ciclos expirados e renova automaticamente"""
    
    db = firestore.Client()
    today = datetime.now().date()
    
    # Buscar planos que expiraram hoje
    expired_plans = db.collection('user_plans').where(
        'end_date', '==', today
    ).where(
        'status', '==', 'active'
    ).stream()
    
    for plan_doc in expired_plans:
        plan = plan_doc.to_dict()
        user_id = plan['user_id']
        
        # Marcar plano atual como completo
        plan_doc.reference.update({
            'status': 'completed',
            'completed_at': datetime.now()
        })
        
        # Criar novo ciclo
        new_plan = {
            'user_id': user_id,
            'cycle_number': plan['cycle_number'] + 1,
            'start_date': today,
            'end_date': today + timedelta(days=45),
            'status': 'awaiting_follow_up',
            'created_at': datetime.now()
        }
        
        db.collection('user_plans').add(new_plan)
        
        # Enviar notificação
        send_cycle_renewal_notification(user_id)
    
    return {'status': 'success', 'processed': len(list(expired_plans))}
```

### **4. Algoritmo de Rebalanceamento (Sistema Full-time)**

```python
# rebalancing_algorithm.py
class CalorieRebalancer:
    """Algoritmo de rebalanceamento calórico inteligente"""
    
    def __init__(self, user_service, plans_service):
        self.user_service = user_service
        self.plans_service = plans_service
    
    async def rebalance_calories(self, user_id: str, excess_calories: float):
        """Rebalanceia calorias excedentes nos próximos dias"""
        
        # 1. Buscar dados do usuário
        user = await self.user_service.get_user(user_id)
        bmr = self.calculate_bmr(user)
        
        # 2. Buscar planos futuros
        future_plans = await self.plans_service.get_future_plans(user_id, days=5)
        
        # 3. Calcular distribuição do déficit
        deficit_distribution = {
            'fat': excess_calories * 0.6,      # 60% das gorduras
            'carbs': excess_calories * 0.3,    # 30% dos carboidratos
            'protein': excess_calories * 0.1   # 10% das proteínas
        }
        
        # 4. Aplicar déficit dia a dia
        remaining_deficit = excess_calories
        
        for day_plan in future_plans:
            if remaining_deficit <= 0:
                break
            
            # Verificar limite de segurança (BMR)
            current_calories = day_plan.total_calories
            max_reduction = max(0, current_calories - bmr)
            
            day_reduction = min(remaining_deficit, max_reduction)
            
            if day_reduction > 0:
                # Aplicar redução proporcional
                self.apply_macro_reduction(day_plan, day_reduction, deficit_distribution)
                remaining_deficit -= day_reduction
                
                # Salvar plano modificado
                await self.plans_service.update_plan(day_plan)
        
        # 5. Log do rebalanceamento
        await self.log_rebalancing(user_id, excess_calories, remaining_deficit)
        
        return remaining_deficit == 0  # True se conseguiu rebalancear tudo
    
    def apply_macro_reduction(self, plan, reduction_calories, distribution):
        """Aplica redução de calorias mantendo proporções"""
        
        for meal in plan.meals:
            meal_proportion = meal.total_calories / plan.total_calories
            meal_reduction = reduction_calories * meal_proportion
            
            # Reduzir macros proporcionalmente
            fat_reduction = meal_reduction * 0.6 / 9  # 9 cal/g
            carb_reduction = meal_reduction * 0.3 / 4  # 4 cal/g
            protein_reduction = meal_reduction * 0.1 / 4  # 4 cal/g
            
            # Aplicar reduções aos alimentos da refeição
            self.reduce_meal_macros(meal, fat_reduction, carb_reduction, protein_reduction)
```

### **5. Interface de Tracking (Flutter)**

```dart
// tracking_screen.dart
class TrackingScreen extends StatefulWidget {
  @override
  _TrackingScreenState createState() => _TrackingScreenState();
}

class _TrackingScreenState extends State<TrackingScreen> {
  DailyBalance _balance = DailyBalance();
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Acompanhamento Diário')),
      body: Column(
        children: [
          // Card de balanço calórico
          BalanceCard(balance: _balance),
          
          // Botões de ação
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  icon: Icon(Icons.fitness_center),
                  label: Text('Atividade Extra'),
                  onPressed: () => _showActivityDialog(),
                ),
              ),
              SizedBox(width: 16),
              Expanded(
                child: ElevatedButton.icon(
                  icon: Icon(Icons.restaurant),
                  label: Text('Alimento Extra'),
                  onPressed: () => _showFoodDialog(),
                ),
              ),
            ],
          ),
          
          // Lista de registros do dia
          Expanded(
            child: TrackingList(entries: _balance.entries),
          ),
        ],
      ),
    );
  }
  
  void _showActivityDialog() {
    showDialog(
      context: context,
      builder: (context) => ActivityRegistrationDialog(
        onActivityAdded: (activity) {
          setState(() {
            _balance.addActivity(activity);
          });
          _checkRebalancing();
        },
      ),
    );
  }
  
  void _checkRebalancing() async {
    if (_balance.hasExcess()) {
      final result = await TrackingService.requestRebalancing(_balance.excess);
      if (result.success) {
        _showRebalancingSuccess();
      }
    }
  }
}
```

## 📊 Cronograma Detalhado

### **Semana 1: Fundação**
- **Dias 1-2**: Popular base de dados TACO
- **Dias 3-4**: Implementar anamnese no Flutter
- **Dias 5-7**: Conectar frontend ao backend

### **Semana 2: Funcionalidades Core**
- **Dias 8-10**: Sistema de ciclos (Cloud Functions)
- **Dias 11-12**: Serviço de equivalência
- **Dias 13-14**: Lista de compras básica

### **Semana 3: Sistema Full-time (Parte 1)**
- **Dias 15-17**: Tracking de atividades extras
- **Dias 18-19**: Tracking de alimentos extras
- **Dias 20-21**: Interface de tracking

### **Semana 4: Sistema Full-time (Parte 2)**
- **Dias 22-24**: Algoritmo de rebalanceamento
- **Dias 25-26**: Validações de segurança
- **Dias 27-28**: Testes extensivos

### **Semana 5: Premium e Polimento**
- **Dias 29-31**: Funcionalidades premium (IA)
- **Dias 32-33**: Sistema de pagamentos
- **Dias 34-35**: Otimizações finais

### **Semana 6: Finalização**
- **Dias 36-38**: Testes de integração
- **Dias 39-40**: Deploy e documentação

## 🎯 Entregáveis por Semana

### **Semana 1**:
- ✅ Base de dados completa (3000+ alimentos)
- ✅ Anamnese funcional no app
- ✅ Geração de planos end-to-end

### **Semana 2**:
- ✅ Renovação automática de ciclos
- ✅ Substituição de alimentos
- ✅ Lista de compras

### **Semana 3**:
- ✅ Registro de atividades/alimentos extras
- ✅ Interface de tracking completa

### **Semana 4**:
- ✅ Rebalanceamento automático funcionando
- ✅ Sistema full-time completo

### **Semana 5**:
- ✅ Funcionalidades premium
- ✅ Sistema de pagamentos

### **Semana 6**:
- ✅ Aplicativo completo e testado
- ✅ Deploy em produção

## 🚀 Próximos Passos Imediatos

### **POSSO COMEÇAR HOJE**:
1. ✅ Popular base de dados TACO
2. ✅ Implementar telas de anamnese
3. ✅ Conectar APIs existentes

### **PRECISO PARA CONTINUAR**:
- ✅ Confirmação para prosseguir
- ✅ Acesso às APIs do Google Cloud
- ✅ Configuração do Firebase

**ESTOU PRONTO PARA COMEÇAR IMEDIATAMENTE!**

O projeto está muito mais avançado do que esperava. Com a base sólida existente, posso entregar um aplicativo completo e funcional em **30-40 dias**.

---
*Plano atualizado baseado na análise dos repositórios existentes*


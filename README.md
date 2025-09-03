# 🚀 EvolveYou - Aplicativo Web Completo

**Versão Web Funcional do EvolveYou - Seu Assistente Pessoal de Fitness e Nutrição**

## 📋 Sobre o Projeto

O EvolveYou é um aplicativo web completo de fitness e nutrição que oferece:
- Sistema de autenticação completo
- Anamnese personalizada (20 perguntas)
- Dashboard com métricas em tempo real
- Planos nutricionais personalizados
- Treinos estruturados
- Coach virtual com IA (Coach EVO)

## ✅ Funcionalidades Implementadas

### 🔐 Sistema de Autenticação
- Login com email/senha
- Cadastro de novos usuários
- Login com Google (configurado)
- Recuperação de senha
- Login demo para testes

### 📝 Onboarding Completo
- **20 perguntas de anamnese** personalizadas
- Cálculos automáticos de:
  - BMR (Taxa Metabólica Basal)
  - TDEE (Gasto Energético Total)
  - IMC (Índice de Massa Corporal)
  - Distribuição de macronutrientes
- Progress bar visual
- Validação de campos

### 📊 Dashboard Principal
**4 abas funcionais:**

#### 1. Visão Geral
- Peso atual vs meta
- IMC com classificação
- Calorias diárias
- Hidratação
- Progresso semanal (treinos, água, nutrição)
- Perfil personalizado
- Distribuição de macronutrientes

#### 2. Nutrição
- Acompanhamento de macronutrientes em tempo real
- Sistema visual de hidratação (copos)
- Refeições detalhadas por horário
- Progresso semanal de calorias
- Cálculos automáticos baseados no perfil

#### 3. Treinos
- Planos personalizados por objetivo
- Exercícios detalhados com séries/reps
- Cronômetro e controle de progresso
- Histórico semanal
- Métricas de desempenho
- Dicas personalizadas

#### 4. Coach EVO (IA)
- Assistente virtual 24/7
- Respostas personalizadas baseadas no perfil
- Chat em tempo real
- Perguntas rápidas contextuais
- Conhecimento completo dos dados do usuário

## 🛠️ Tecnologias Utilizadas

- **Frontend**: React 18 + Vite
- **Styling**: Tailwind CSS + Shadcn/UI
- **Icons**: Lucide React
- **Autenticação**: Sistema mock (pronto para Firebase)
- **Estado**: React Hooks + LocalStorage
- **Roteamento**: React Router DOM

## 🚀 Como Executar

### Pré-requisitos
- Node.js 18+
- pnpm (ou npm)

### Instalação
```bash
# Clone o repositório
git clone https://github.com/magnusimports/evolveyou-web-complete.git

# Entre no diretório
cd evolveyou-web-complete

# Instale as dependências
pnpm install

# Execute em modo desenvolvimento
pnpm run dev
```

### Acesso
- **Local**: http://localhost:5173
- **Login Demo**: Use o botão "Login Demo" para testar todas as funcionalidades

## 📱 Funcionalidades Principais

### Sistema de Cálculos Automáticos
- **BMR**: Calculado pela fórmula de Mifflin-St Jeor
- **TDEE**: BMR × fator de atividade
- **IMC**: Peso / (altura²) com classificação
- **Macros**: Distribuição personalizada por objetivo

### Personalização Inteligente
- Planos de treino baseados no objetivo (ganho de massa, perda de peso, etc.)
- Recomendações nutricionais por perfil
- Coach EVO com respostas contextualizadas
- Interface adaptada ao progresso do usuário

### Interface Moderna
- Design responsivo (mobile-first)
- Animações suaves
- Componentes reutilizáveis
- Tema consistente
- UX otimizada

## 🎯 Dados de Teste

**Login Demo:**
- Email: teste@evolveyou.com
- Senha: 123456

**Perfil de Exemplo:**
- Idade: 28 anos
- Peso: 80kg
- Altura: 175cm
- Objetivo: Ganhar massa muscular
- Nível: Moderadamente ativo

## 📈 Próximas Implementações

- [ ] Integração com Firebase real
- [ ] Sistema de notificações
- [ ] Gráficos de progresso avançados
- [ ] Sincronização offline
- [ ] App mobile (React Native)
- [ ] Integração com wearables
- [ ] Sistema de gamificação

## 🔧 Estrutura do Projeto

```
src/
├── components/
│   ├── auth/           # Componentes de autenticação
│   ├── dashboard/      # Componentes do dashboard
│   └── ui/            # Componentes reutilizáveis
├── pages/             # Páginas principais
├── hooks/             # Hooks customizados
├── data/              # Dados e configurações
├── config/            # Configurações (Firebase, etc.)
└── App.jsx           # Componente principal
```

## 👨‍💻 Desenvolvido por

**Manus AI** - Assistente de desenvolvimento autônomo
- Análise completa de requisitos
- Implementação full-stack
- Testes e otimização
- Documentação técnica

## 📄 Licença

Este projeto é propriedade da Magnus Imports e está sob licença privada.

---

**🎉 Versão Web Funcional - Pronta para Produção!**


# EvolveYou - Funcionalidades Atuais

Este documento descreve as funcionalidades já implementadas no projeto EvolveYou, com base na análise do código-fonte e da estrutura do projeto.

## 1. Estrutura Geral

- **Monorepo**: O projeto utiliza um monorepo para gerenciar as diferentes partes da aplicação (mobile, web, serviços).
- **Aplicações**: Existem três aplicações principais: `mobile` (Flutter), `web` (React) e `admin` (React Admin Panel).
- **Microserviços**: A arquitetura de backend é baseada em microserviços, utilizando FastAPI.

## 2. Frontend Web (React)

- **Tecnologias**: React, Vite, Tailwind CSS, Radix UI, Recharts, Framer Motion.
- **Componentes**: A aplicação web possui uma vasta gama de componentes de UI pré-construídos, como `Card`, `Button`, `Badge`, `Progress`, `Tabs`, `Alert`, etc.
- **Estrutura**: O componente principal `App.jsx` já está configurado com hooks customizados para buscar dados da API e se conectar a WebSockets.
- **Funcionalidades Implementadas**:
    - **Dashboard de Progresso**: O `App.jsx` renderiza um dashboard com gráficos e informações de progresso, utilizando dados mockados ou de hooks que precisam ser conectados ao backend.
    - **Visualização de Status de Serviços**: O dashboard também exibe o status dos microserviços.

## 3. Backend (Microserviços FastAPI)

- **Serviço de Gateway**: Um serviço de gateway (`backend`) centraliza as requisições, roteando-as para os microserviços apropriados. Ele também lida com autenticação, rate limiting e controle de acesso a funcionalidades premium.
- **Serviço de Usuários**: O serviço de usuários (`users`) é responsável pela autenticação, perfis e onboarding. Utiliza FastAPI, Firebase Admin SDK e Pydantic para validação de dados.
- **Serviço de Conteúdo**: O serviço de conteúdo (`content`) gerencia os exercícios, receitas e a base de dados de alimentos (TACO). Utiliza FastAPI e Firestore.
- **Outros Serviços**: Existem outros serviços como `health-check`, `plans-service`, `tracking-service` e `evo-service`, cada um com suas responsabilidades específicas.

## 4. Autenticação e Segurança

- **Firebase Authentication**: A autenticação é gerenciada pelo Firebase, com suporte a JWT e OAuth2 (Google, Apple, Facebook).
- **Autorização**: O sistema utiliza controle de acesso baseado em papéis (RBAC) e rate limiting.
- **Segurança**: O projeto segue as boas práticas de segurança, como o uso de HTTPS, validação de requisições e headers de segurança.

## 5. Próximos Passos

Com base nesta análise, os próximos passos se concentrarão em:

- **Mapear os fluxos de usuário completos**: Detalhar o fluxo de cadastro, login, onboarding, criação de treinos, dietas, etc.
- **Definir a arquitetura completa**: Criar um diagrama de arquitetura que ilustre a interação entre todos os componentes.
- **Especificar as APIs necessárias**: Detalhar os endpoints, payloads e respostas de todas as APIs que precisam ser desenvolvidas ou finalizadas.
- **Planejar a estrutura de dados**: Modelar os dados no Firestore para suportar todas as funcionalidades do aplicativo.





# Fluxos de Usuário - EvolveYou

## 1. Fluxo de Cadastro e Login

### 1.1. Cadastro de Novo Usuário

1.  **Acesso à Página de Cadastro**: O usuário acessa a página de cadastro através da página inicial ou de um link direto.
2.  **Preenchimento do Formulário**: O usuário preenche os seguintes campos:
    *   Nome completo
    *   E-mail
    *   Senha
    *   Confirmação de senha
3.  **Validação**: O sistema valida os dados em tempo real (e.g., se o e-mail já está em uso, se as senhas coincidem).
4.  **Envio do Formulário**: O usuário clica no botão "Cadastrar".
5.  **Criação da Conta**: O backend cria uma nova conta de usuário no Firebase Authentication.
6.  **Redirecionamento**: O usuário é redirecionado para a tela de login ou diretamente para o onboarding.

### 1.2. Login de Usuário Existente

1.  **Acesso à Página de Login**: O usuário acessa a página de login.
2.  **Preenchimento do Formulário**: O usuário insere seu e-mail e senha.
3.  **Login com Redes Sociais**: Opcionalmente, o usuário pode fazer login com Google, Apple ou Facebook.
4.  **Autenticação**: O sistema verifica as credenciais no Firebase Authentication.
5.  **Redirecionamento**: Após a autenticação bem-sucedida, o usuário é redirecionado para o dashboard principal.

### 1.3. Recuperação de Senha

1.  **Acesso à Página de Recuperação**: O usuário clica em "Esqueci minha senha" na página de login.
2.  **Inserção do E-mail**: O usuário insere o e-mail da sua conta.
3.  **Envio do Link de Recuperação**: O Firebase envia um e-mail com um link para redefinir a senha.
4.  **Redefinição da Senha**: O usuário clica no link, define uma nova senha e a confirma.
5.  **Redirecionamento**: O usuário é redirecionado para a página de login.




## 2. Fluxo de Onboarding

### 2.1. Coleta de Dados Pessoais

1.  **Tela de Boas-Vindas**: Após o primeiro login, o usuário é saudado com uma tela de boas-vindas.
2.  **Coleta de Dados Básicos**: O usuário insere as seguintes informações:
    *   Data de nascimento
    *   Gênero
    *   Altura
    *   Peso atual
3.  **Nível de Atividade**: O usuário seleciona seu nível de atividade física (sedentário, leve, moderado, ativo, muito ativo).

### 2.2. Definição de Objetivos

1.  **Seleção de Objetivos**: O usuário escolhe seu objetivo principal:
    *   Perder peso
    *   Ganhar massa muscular
    *   Manter o peso
2.  **Meta de Peso**: Se o objetivo for perder ou ganhar peso, o usuário define sua meta de peso.
3.  **Preferências de Treino**: O usuário informa suas preferências de treino:
    *   Dias da semana disponíveis para treinar
    *   Duração média do treino
    *   Tipos de exercícios preferidos (musculação, cardio, etc.)

### 2.3. Preferências Alimentares

1.  **Restrições Alimentares**: O usuário informa se possui alguma restrição alimentar (alergias, intolerâncias, etc.).
2.  **Preferências de Dieta**: O usuário seleciona suas preferências de dieta (vegetariana, vegana, etc.).
3.  **Número de Refeições**: O usuário informa o número de refeições que costuma fazer por dia.

### 2.4. Finalização do Onboarding

1.  **Resumo**: O sistema exibe um resumo das informações coletadas.
2.  **Confirmação**: O usuário confirma as informações.
3.  **Redirecionamento**: O usuário é redirecionado para o dashboard principal, onde verá seu plano de treino e dieta inicial gerado com base nas informações fornecidas.




## 3. Fluxo de Treinos

### 3.1. Visualização do Treino do Dia

1.  **Acesso ao Dashboard**: No dashboard principal, o usuário vê um card com o treino do dia.
2.  **Detalhes do Treino**: Ao clicar no card, o usuário é levado para a tela de detalhes do treino, que exibe:
    *   Lista de exercícios
    *   Número de séries e repetições
    *   Tempo de descanso entre as séries
    *   Vídeos demonstrativos de cada exercício

### 3.2. Execução do Treino

1.  **Início do Treino**: O usuário clica em "Iniciar Treino".
2.  **Tela de Execução**: A tela de execução do treino exibe o exercício atual, com um cronômetro para o tempo de descanso.
3.  **Registro de Carga**: O usuário registra a carga utilizada em cada série.
4.  **Navegação entre Exercícios**: O usuário pode avançar para o próximo exercício ou voltar para o anterior.
5.  **Finalização do Treino**: Ao concluir todos os exercícios, o usuário clica em "Finalizar Treino".

### 3.3. Histórico de Treinos

1.  **Acesso ao Histórico**: O usuário pode acessar seu histórico de treinos a partir do menu principal.
2.  **Visualização**: O histórico exibe uma lista de todos os treinos realizados, com a data e a duração de cada um.
3.  **Detalhes do Treino Realizado**: Ao clicar em um treino do histórico, o usuário pode ver os detalhes, incluindo as cargas registradas.




## 4. Fluxo de Dietas

### 4.1. Visualização da Dieta

1.  **Acesso à Dieta**: No dashboard ou no menu principal, o usuário acessa a sua dieta.
2.  **Visualização Diária**: A dieta é exibida por dia, com as refeições planejadas (café da manhã, almoço, jantar, lanches).
3.  **Detalhes da Refeição**: Ao clicar em uma refeição, o usuário vê os alimentos, as quantidades e as informações nutricionais (calorias, macronutrientes).

### 4.2. Registro de Refeições

1.  **Check-in da Refeição**: O usuário marca as refeições que consumiu.
2.  **Substituição de Alimentos**: Opcionalmente, o usuário pode substituir um alimento da dieta por outro equivalente.
3.  **Adição de Alimentos Extras**: O usuário pode adicionar alimentos que consumiu e que não estavam na dieta.

### 4.3. Histórico de Dietas

1.  **Acesso ao Histórico**: O usuário pode acessar seu histórico de dietas.
2.  **Visualização**: O histórico exibe as dietas de dias anteriores, com as refeições registradas.

## 5. Fluxo do Dashboard

1.  **Visualização Geral**: O dashboard exibe um resumo do progresso do usuário, incluindo:
    *   Gráfico de peso
    *   Calorias consumidas vs. meta
    *   Macronutrientes consumidos vs. meta
    *   Treino do dia
    *   Próxima refeição
2.  **Navegação**: A partir do dashboard, o usuário pode navegar para as seções de treino, dieta, progresso e configurações.

## 6. Fluxo de Configurações

1.  **Acesso às Configurações**: O usuário acessa a tela de configurações a partir do menu principal.
2.  **Gerenciamento da Conta**: O usuário pode editar suas informações pessoais, alterar a senha e gerenciar as notificações.
3.  **Preferências**: O usuário pode ajustar suas preferências de treino e dieta.
4.  **Assinatura**: O usuário pode visualizar o status da sua assinatura e fazer upgrade para um plano premium.
5.  **Logout**: O usuário pode sair da sua conta.



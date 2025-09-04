# Especificação de APIs - EvolveYou

Este documento detalha os endpoints, payloads e respostas das APIs necessárias para o funcionamento do EvolveYou.




## 1. Users Service

### 1.1. Autenticação

-   **POST /api/users/register**
    -   **Descrição**: Registra um novo usuário.
    -   **Payload**:
        ```json
        {
            "name": "string",
            "email": "string",
            "password": "string"
        }
        ```
    -   **Resposta (201)**:
        ```json
        {
            "uid": "string",
            "email": "string",
            "name": "string"
        }
        ```

-   **POST /api/users/login**
    -   **Descrição**: Autentica um usuário e retorna um token JWT.
    -   **Payload**:
        ```json
        {
            "email": "string",
            "password": "string"
        }
        ```
    -   **Resposta (200)**:
        ```json
        {
            "access_token": "string",
            "token_type": "bearer"
        }
        ```

-   **POST /api/users/login/google**
    -   **Descrição**: Autentica um usuário com o Google e retorna um token JWT.
    -   **Payload**:
        ```json
        {
            "id_token": "string"
        }
        ```
    -   **Resposta (200)**:
        ```json
        {
            "access_token": "string",
            "token_type": "bearer"
        }
        ```

### 1.2. Perfil do Usuário

-   **GET /api/users/me**
    -   **Descrição**: Retorna os dados do usuário autenticado.
    -   **Autenticação**: Bearer Token
    -   **Resposta (200)**:
        ```json
        {
            "uid": "string",
            "name": "string",
            "email": "string",
            "onboarding_completed": "boolean",
            "profile": {
                "birth_date": "string",
                "gender": "string",
                "height": "number",
                "weight": "number",
                "activity_level": "string",
                "goal": "string",
                "target_weight": "number"
            }
        }
        ```

-   **PUT /api/users/me**
    -   **Descrição**: Atualiza os dados do usuário autenticado.
    -   **Autenticação**: Bearer Token
    -   **Payload**:
        ```json
        {
            "name": "string",
            "profile": {
                "birth_date": "string",
                "gender": "string",
                "height": "number",
                "weight": "number",
                "activity_level": "string",
                "goal": "string",
                "target_weight": "number"
            }
        }
        ```
    -   **Resposta (200)**:
        ```json
        {
            "message": "Profile updated successfully"
        }
        ```




## 2. Content Service

### 2.1. Exercícios

-   **GET /api/content/exercises**
    -   **Descrição**: Retorna uma lista de exercícios.
    -   **Query Params**:
        -   `muscle_group`: `string` (opcional) - Filtra por grupo muscular.
        -   `difficulty`: `string` (opcional) - Filtra por dificuldade (iniciante, intermediário, avançado).
    -   **Resposta (200)**:
        ```json
        [
            {
                "id": "string",
                "name": "string",
                "muscle_group": "string",
                "difficulty": "string",
                "video_url": "string"
            }
        ]
        ```

-   **GET /api/content/exercises/{exercise_id}**
    -   **Descrição**: Retorna os detalhes de um exercício específico.
    -   **Resposta (200)**:
        ```json
        {
            "id": "string",
            "name": "string",
            "muscle_group": "string",
            "difficulty": "string",
            "description": "string",
            "video_url": "string"
        }
        ```

### 2.2. Receitas

-   **GET /api/content/recipes**
    -   **Descrição**: Retorna uma lista de receitas.
    -   **Query Params**:
        -   `meal_type`: `string` (opcional) - Filtra por tipo de refeição (café da manhã, almoço, etc.).
        -   `dietary_preference`: `string` (opcional) - Filtra por preferência alimentar (vegetariana, vegana, etc.).
    -   **Resposta (200)**:
        ```json
        [
            {
                "id": "string",
                "name": "string",
                "meal_type": "string",
                "dietary_preference": "string",
                "calories": "number"
            }
        ]
        ```

-   **GET /api/content/recipes/{recipe_id}**
    -   **Descrição**: Retorna os detalhes de uma receita específica.
    -   **Resposta (200)**:
        ```json
        {
            "id": "string",
            "name": "string",
            "meal_type": "string",
            "dietary_preference": "string",
            "ingredients": "array",
            "instructions": "string",
            "calories": "number",
            "protein": "number",
            "carbs": "number",
            "fat": "number"
        }
        ```




## 3. Plans Service

### 3.1. Plano de Treino

-   **GET /api/plans/workout**
    -   **Descrição**: Retorna o plano de treino do usuário para a semana atual.
    -   **Autenticação**: Bearer Token
    -   **Resposta (200)**:
        ```json
        {
            "weekly_plan": [
                {
                    "day_of_week": "string",
                    "workout": {
                        "name": "string",
                        "exercises": [
                            {
                                "exercise_id": "string",
                                "name": "string",
                                "sets": "number",
                                "reps": "string"
                            }
                        ]
                    }
                }
            ]
        }
        ```

### 3.2. Plano de Dieta

-   **GET /api/plans/diet**
    -   **Descrição**: Retorna o plano de dieta do usuário para o dia atual.
    -   **Autenticação**: Bearer Token
    -   **Resposta (200)**:
        ```json
        {
            "daily_plan": {
                "date": "string",
                "meals": [
                    {
                        "meal_type": "string",
                        "recipe_id": "string",
                        "name": "string",
                        "calories": "number"
                    }
                ]
            }
        }
        ```

## 4. Tracking Service

### 4.1. Registro de Treino

-   **POST /api/tracking/workouts**
    -   **Descrição**: Registra um treino realizado pelo usuário.
    -   **Autenticação**: Bearer Token
    -   **Payload**:
        ```json
        {
            "workout_id": "string",
            "date": "string",
            "duration_minutes": "number",
            "exercises": [
                {
                    "exercise_id": "string",
                    "sets": [
                        {
                            "reps": "number",
                            "weight": "number"
                        }
                    ]
                }
            ]
        }
        ```
    -   **Resposta (201)**:
        ```json
        {
            "message": "Workout tracked successfully"
        }
        ```

### 4.2. Registro de Dieta

-   **POST /api/tracking/meals**
    -   **Descrição**: Registra uma refeição consumida pelo usuário.
    -   **Autenticação**: Bearer Token
    -   **Payload**:
        ```json
        {
            "meal_id": "string",
            "date": "string",
            "consumed": "boolean"
        }
        ```
    -   **Resposta (201)**:
        ```json
        {
            "message": "Meal tracked successfully"
        }
        ```

### 4.3. Registro de Peso

-   **POST /api/tracking/weight**
    -   **Descrição**: Registra o peso do usuário.
    -   **Autenticação**: Bearer Token
    -   **Payload**:
        ```json
        {
            "weight": "number",
            "date": "string"
        }
        ```
    -   **Resposta (201)**:
        ```json
        {
            "message": "Weight tracked successfully"
        }
        ```
        ```
        ```
        ```


# Estrutura de Dados - Firestore

Este documento descreve a estrutura de dados utilizada no Firestore para o projeto EvolveYou.




## Coleções Principais

### 1. `users`

-   **Descrição**: Armazena os dados dos usuários.
-   **Documento**: `uid` (ID do usuário no Firebase Auth)
-   **Campos**:
    -   `name`: `string`
    -   `email`: `string`
    -   `onboarding_completed`: `boolean`
    -   `profile`: `map`
        -   `birth_date`: `timestamp`
        -   `gender`: `string`
        -   `height`: `number`
        -   `weight`: `number`
        -   `activity_level`: `string`
        -   `goal`: `string`
        -   `target_weight`: `number`

### 2. `workouts`

-   **Descrição**: Armazena os planos de treino dos usuários.
-   **Documento**: `uid` (ID do usuário)
-   **Subcoleção**: `weekly_plans`
    -   **Documento**: `plan_id` (ID do plano semanal)
    -   **Campos**:
        -   `start_date`: `timestamp`
        -   `end_date`: `timestamp`
        -   `days`: `array`
            -   `day_of_week`: `string`
            -   `workout_name`: `string`
            -   `exercises`: `array`
                -   `exercise_id`: `string` (referência à coleção `exercises`)
                -   `name`: `string`
                -   `sets`: `number`
                -   `reps`: `string`

### 3. `diets`

-   **Descrição**: Armazena os planos de dieta dos usuários.
-   **Documento**: `uid` (ID do usuário)
-   **Subcoleção**: `daily_plans`
    -   **Documento**: `date` (data do plano diário)
    -   **Campos**:
        -   `meals`: `array`
            -   `meal_type`: `string`
            -   `recipe_id`: `string` (referência à coleção `recipes`)
            -   `name`: `string`
            -   `calories`: `number`

### 4. `tracking`

-   **Descrição**: Armazena os dados de progresso dos usuários.
-   **Documento**: `uid` (ID do usuário)
-   **Subcoleções**:
    -   `workouts`
        -   **Documento**: `workout_log_id`
        -   **Campos**: `workout_id`, `date`, `duration_minutes`, `exercises`
    -   `meals`
        -   **Documento**: `meal_log_id`
        -   **Campos**: `meal_id`, `date`, `consumed`
    -   `weight`
        -   **Documento**: `weight_log_id`
        -   **Campos**: `weight`, `date`

### 5. `exercises`

-   **Descrição**: Armazena os detalhes dos exercícios.
-   **Documento**: `exercise_id`
-   **Campos**: `name`, `muscle_group`, `difficulty`, `description`, `video_url`

### 6. `recipes`

-   **Descrição**: Armazena os detalhes das receitas.
-   **Documento**: `recipe_id`
-   **Campos**: `name`, `meal_type`, `dietary_preference`, `ingredients`, `instructions`, `calories`, `protein`, `carbs`, `fat`



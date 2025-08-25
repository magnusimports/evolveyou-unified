const { test, expect } = require('@playwright/test');

test.describe('EvolveYou User Flow', () => {
  let testUser;
  
  test.beforeEach(async ({ page }) => {
    // Gerar dados de usuário únicos para cada teste
    const timestamp = Date.now();
    testUser = {
      email: `test${timestamp}@evolveyou.com.br`,
      password: 'TestPassword123!',
      fullName: 'Usuário Teste E2E',
      dateOfBirth: '01/01/1990'
    };
    
    // Navegar para a página inicial
    await page.goto('/');
    
    // Aguardar carregamento da página
    await page.waitForLoadState('networkidle');
  });

  test('Complete user registration and onboarding flow', async ({ page }) => {
    // 1. LANDING PAGE
    await test.step('Navigate to landing page', async () => {
      await expect(page).toHaveTitle(/EvolveYou/);
      
      // Verificar elementos principais da landing page
      await expect(page.locator('h1')).toContainText('EvolveYou');
      await expect(page.locator('[data-testid="cta-button"]')).toBeVisible();
    });

    // 2. REGISTRO
    await test.step('User registration', async () => {
      // Clicar no botão de registro
      await page.click('[data-testid="register-button"]');
      
      // Aguardar modal ou página de registro
      await page.waitForSelector('[data-testid="register-form"]');
      
      // Preencher formulário de registro
      await page.fill('[data-testid="email-input"]', testUser.email);
      await page.fill('[data-testid="password-input"]', testUser.password);
      await page.fill('[data-testid="confirm-password-input"]', testUser.password);
      await page.fill('[data-testid="full-name-input"]', testUser.fullName);
      
      // Aceitar termos
      await page.check('[data-testid="terms-checkbox"]');
      
      // Submeter formulário
      await page.click('[data-testid="submit-register"]');
      
      // Aguardar redirecionamento ou sucesso
      await page.waitForURL('**/onboarding**', { timeout: 30000 });
    });

    // 3. ONBOARDING - DADOS PESSOAIS
    await test.step('Personal information onboarding', async () => {
      await expect(page.locator('[data-testid="onboarding-step-1"]')).toBeVisible();
      
      // Preencher dados pessoais
      await page.fill('[data-testid="date-of-birth"]', testUser.dateOfBirth);
      await page.selectOption('[data-testid="gender-select"]', 'masculino');
      await page.fill('[data-testid="height-input"]', '175');
      await page.fill('[data-testid="weight-input"]', '70');
      
      // Próximo passo
      await page.click('[data-testid="next-step"]');
      await page.waitForSelector('[data-testid="onboarding-step-2"]');
    });

    // 4. ONBOARDING - OBJETIVOS
    await test.step('Goals onboarding', async () => {
      await expect(page.locator('[data-testid="onboarding-step-2"]')).toBeVisible();
      
      // Selecionar objetivo principal
      await page.click('[data-testid="goal-ganho-massa"]');
      
      // Definir peso alvo
      await page.fill('[data-testid="target-weight"]', '75');
      
      // Selecionar prazo
      await page.selectOption('[data-testid="timeline-select"]', '12');
      
      // Próximo passo
      await page.click('[data-testid="next-step"]');
      await page.waitForSelector('[data-testid="onboarding-step-3"]');
    });

    // 5. ONBOARDING - ATIVIDADE FÍSICA
    await test.step('Activity level onboarding', async () => {
      await expect(page.locator('[data-testid="onboarding-step-3"]')).toBeVisible();
      
      // Selecionar nível de atividade
      await page.click('[data-testid="activity-moderadamente-ativo"]');
      
      // Frequência de treino
      await page.selectOption('[data-testid="training-frequency"]', '4');
      
      // Experiência
      await page.click('[data-testid="experience-intermediario"]');
      
      // Próximo passo
      await page.click('[data-testid="next-step"]');
      await page.waitForSelector('[data-testid="onboarding-step-4"]');
    });

    // 6. ONBOARDING - PREFERÊNCIAS
    await test.step('Preferences onboarding', async () => {
      await expect(page.locator('[data-testid="onboarding-step-4"]')).toBeVisible();
      
      // Exercícios preferidos
      await page.check('[data-testid="exercise-musculacao"]');
      await page.check('[data-testid="exercise-cardio"]');
      
      // Equipamentos disponíveis
      await page.check('[data-testid="equipment-academia"]');
      
      // Restrições alimentares
      await page.click('[data-testid="no-dietary-restrictions"]');
      
      // Finalizar onboarding
      await page.click('[data-testid="finish-onboarding"]');
      
      // Aguardar processamento
      await page.waitForSelector('[data-testid="onboarding-success"]', { timeout: 30000 });
    });

    // 7. DASHBOARD
    await test.step('Access dashboard', async () => {
      // Aguardar redirecionamento para dashboard
      await page.waitForURL('**/dashboard**', { timeout: 30000 });
      
      // Verificar elementos do dashboard
      await expect(page.locator('[data-testid="welcome-message"]')).toContainText(testUser.fullName);
      await expect(page.locator('[data-testid="calorie-goal"]')).toBeVisible();
      await expect(page.locator('[data-testid="workout-plan"]')).toBeVisible();
      await expect(page.locator('[data-testid="nutrition-plan"]')).toBeVisible();
    });

    // 8. NAVEGAÇÃO PRINCIPAL
    await test.step('Navigate main sections', async () => {
      // Treinos
      await page.click('[data-testid="nav-workouts"]');
      await page.waitForSelector('[data-testid="workouts-page"]');
      await expect(page.locator('[data-testid="workout-list"]')).toBeVisible();
      
      // Nutrição
      await page.click('[data-testid="nav-nutrition"]');
      await page.waitForSelector('[data-testid="nutrition-page"]');
      await expect(page.locator('[data-testid="meal-plan"]')).toBeVisible();
      
      // Progresso
      await page.click('[data-testid="nav-progress"]');
      await page.waitForSelector('[data-testid="progress-page"]');
      await expect(page.locator('[data-testid="progress-charts"]')).toBeVisible();
      
      // Perfil
      await page.click('[data-testid="nav-profile"]');
      await page.waitForSelector('[data-testid="profile-page"]');
      await expect(page.locator('[data-testid="profile-info"]')).toContainText(testUser.email);
    });
  });

  test('Workout tracking flow', async ({ page }) => {
    // Primeiro fazer login (simplificado para este teste)
    await test.step('Login', async () => {
      await page.goto('/login');
      await page.fill('[data-testid="email-input"]', 'demo@evolveyou.com.br');
      await page.fill('[data-testid="password-input"]', 'demo123');
      await page.click('[data-testid="login-button"]');
      await page.waitForURL('**/dashboard**');
    });

    // Iniciar treino
    await test.step('Start workout', async () => {
      await page.click('[data-testid="nav-workouts"]');
      await page.waitForSelector('[data-testid="workouts-page"]');
      
      // Selecionar primeiro treino disponível
      await page.click('[data-testid="workout-card"]:first-child');
      await page.waitForSelector('[data-testid="workout-details"]');
      
      // Iniciar treino
      await page.click('[data-testid="start-workout"]');
      await page.waitForSelector('[data-testid="workout-session"]');
    });

    // Executar exercícios
    await test.step('Complete exercises', async () => {
      // Primeiro exercício
      await expect(page.locator('[data-testid="current-exercise"]')).toBeVisible();
      
      // Registrar série
      await page.fill('[data-testid="weight-input"]', '60');
      await page.fill('[data-testid="reps-input"]', '12');
      await page.click('[data-testid="complete-set"]');
      
      // Aguardar próxima série ou exercício
      await page.waitForTimeout(2000);
      
      // Completar mais algumas séries (simplificado)
      for (let i = 0; i < 2; i++) {
        await page.fill('[data-testid="weight-input"]', '60');
        await page.fill('[data-testid="reps-input"]', '10');
        await page.click('[data-testid="complete-set"]');
        await page.waitForTimeout(1000);
      }
    });

    // Finalizar treino
    await test.step('Finish workout', async () => {
      await page.click('[data-testid="finish-workout"]');
      
      // Aguardar resumo do treino
      await page.waitForSelector('[data-testid="workout-summary"]');
      
      // Verificar dados do resumo
      await expect(page.locator('[data-testid="total-duration"]')).toBeVisible();
      await expect(page.locator('[data-testid="exercises-completed"]')).toBeVisible();
      await expect(page.locator('[data-testid="total-volume"]')).toBeVisible();
      
      // Salvar treino
      await page.click('[data-testid="save-workout"]');
      
      // Aguardar confirmação
      await expect(page.locator('[data-testid="workout-saved"]')).toBeVisible();
    });
  });

  test('Nutrition logging flow', async ({ page }) => {
    // Login simplificado
    await test.step('Login', async () => {
      await page.goto('/login');
      await page.fill('[data-testid="email-input"]', 'demo@evolveyou.com.br');
      await page.fill('[data-testid="password-input"]', 'demo123');
      await page.click('[data-testid="login-button"]');
      await page.waitForURL('**/dashboard**');
    });

    // Acessar seção de nutrição
    await test.step('Access nutrition section', async () => {
      await page.click('[data-testid="nav-nutrition"]');
      await page.waitForSelector('[data-testid="nutrition-page"]');
      
      // Verificar plano nutricional
      await expect(page.locator('[data-testid="daily-calories"]')).toBeVisible();
      await expect(page.locator('[data-testid="macros-breakdown"]')).toBeVisible();
    });

    // Adicionar refeição
    await test.step('Add meal', async () => {
      await page.click('[data-testid="add-meal-button"]');
      await page.waitForSelector('[data-testid="meal-modal"]');
      
      // Selecionar tipo de refeição
      await page.selectOption('[data-testid="meal-type"]', 'cafe_da_manha');
      
      // Buscar alimento
      await page.fill('[data-testid="food-search"]', 'arroz');
      await page.waitForSelector('[data-testid="food-results"]');
      
      // Selecionar primeiro resultado
      await page.click('[data-testid="food-item"]:first-child');
      
      // Definir quantidade
      await page.fill('[data-testid="food-quantity"]', '100');
      
      // Adicionar à refeição
      await page.click('[data-testid="add-food"]');
      
      // Salvar refeição
      await page.click('[data-testid="save-meal"]');
      
      // Aguardar atualização
      await page.waitForSelector('[data-testid="meal-added"]');
    });

    // Verificar atualização das calorias
    await test.step('Verify calorie update', async () => {
      // Aguardar atualização dos valores
      await page.waitForTimeout(2000);
      
      // Verificar se as calorias foram atualizadas
      const caloriesConsumed = await page.textContent('[data-testid="calories-consumed"]');
      expect(parseInt(caloriesConsumed)).toBeGreaterThan(0);
      
      // Verificar progresso das macros
      await expect(page.locator('[data-testid="protein-progress"]')).toBeVisible();
      await expect(page.locator('[data-testid="carbs-progress"]')).toBeVisible();
      await expect(page.locator('[data-testid="fat-progress"]')).toBeVisible();
    });
  });

  test('Mobile responsive design', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Este teste é apenas para mobile');

    await test.step('Mobile navigation', async () => {
      await page.goto('/');
      
      // Verificar se o menu mobile está presente
      await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible();
      
      // Abrir menu mobile
      await page.click('[data-testid="mobile-menu-button"]');
      await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
      
      // Testar navegação mobile
      await page.click('[data-testid="mobile-nav-workouts"]');
      await page.waitForURL('**/workouts**');
    });

    await test.step('Mobile forms', async () => {
      // Testar formulários em mobile
      await page.goto('/register');
      
      // Verificar se inputs são adequados para mobile
      const emailInput = page.locator('[data-testid="email-input"]');
      await expect(emailInput).toHaveAttribute('type', 'email');
      
      const passwordInput = page.locator('[data-testid="password-input"]');
      await expect(passwordInput).toHaveAttribute('type', 'password');
    });
  });

  test('Performance and loading', async ({ page }) => {
    await test.step('Page load performance', async () => {
      const startTime = Date.now();
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const loadTime = Date.now() - startTime;
      
      // Página deve carregar em menos de 5 segundos
      expect(loadTime).toBeLessThan(5000);
    });

    await test.step('API response times', async () => {
      // Interceptar requisições da API
      const apiRequests = [];
      
      page.on('response', response => {
        if (response.url().includes('/api/')) {
          apiRequests.push({
            url: response.url(),
            status: response.status(),
            timing: response.timing()
          });
        }
      });
      
      // Navegar e fazer algumas ações
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // Verificar se as APIs responderam adequadamente
      for (const request of apiRequests) {
        expect(request.status).toBeLessThan(400);
        // APIs devem responder em menos de 2 segundos
        expect(request.timing).toBeLessThan(2000);
      }
    });
  });
});


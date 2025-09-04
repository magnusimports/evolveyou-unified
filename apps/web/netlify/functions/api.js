const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
  // Configurar CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Responder a requisições OPTIONS (CORS preflight)
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  try {
    // Simular respostas da API baseadas no path
    const apiPath = event.path.replace('/.netlify/functions/api', '');
    
    // Endpoint de saúde
    if (apiPath === '/health') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'healthy',
          service: 'EvolveYou Backend',
          version: '1.0.0',
          database: 'netlify',
          timestamp: new Date().toISOString()
        })
      };
    }

    // Endpoint de registro
    if (apiPath === '/auth/register' && event.httpMethod === 'POST') {
      const data = JSON.parse(event.body || '{}');
      
      return {
        statusCode: 201,
        headers,
        body: JSON.stringify({
          message: 'Usuário registrado com sucesso',
          access_token: 'demo_token_' + Math.random().toString(36).substr(2, 9),
          user: {
            id: 1,
            name: data.name || 'Usuário',
            email: data.email,
            onboarding_completed: false
          }
        })
      };
    }

    // Endpoint de login
    if (apiPath === '/auth/login' && event.httpMethod === 'POST') {
      const data = JSON.parse(event.body || '{}');
      
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          message: 'Login realizado com sucesso',
          access_token: 'demo_token_' + Math.random().toString(36).substr(2, 9),
          user: {
            id: 1,
            name: 'João Silva',
            email: data.email,
            onboarding_completed: true
          }
        })
      };
    }

    // Endpoint de usuário atual
    if (apiPath === '/auth/me') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          id: 1,
          name: 'João Silva',
          email: 'joao@evolveyou.com',
          onboarding_completed: true
        })
      };
    }

    // Endpoint de onboarding
    if (apiPath === '/auth/onboarding' && event.httpMethod === 'POST') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          message: 'Onboarding completado com sucesso',
          user: {
            id: 1,
            name: 'João Silva',
            email: 'joao@evolveyou.com',
            onboarding_completed: true
          }
        })
      };
    }

    // Endpoint de exercícios
    if (apiPath === '/content/exercises') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          exercises: [
            {
              id: 1,
              name: 'Supino Reto',
              muscle_group: 'Peito',
              difficulty: 'Intermediário',
              equipment: 'Barra'
            },
            {
              id: 2,
              name: 'Agachamento',
              muscle_group: 'Pernas',
              difficulty: 'Iniciante',
              equipment: 'Peso corporal'
            }
          ]
        })
      };
    }

    // Endpoint de receitas
    if (apiPath === '/content/recipes') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          recipes: [
            {
              id: 1,
              name: 'Frango Grelhado',
              meal_type: 'Almoço',
              calories: 250,
              protein: 30
            }
          ]
        })
      };
    }

    // Endpoint de plano de treino
    if (apiPath === '/plans/workout') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          week: [
            {
              day: 'Segunda',
              focus: 'Peito e Tríceps',
              exercises: [
                { name: 'Supino Reto', sets: 3, reps: '8-12' }
              ]
            }
          ]
        })
      };
    }

    // Endpoint de plano de dieta
    if (apiPath === '/plans/diet') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          daily_calories: 2000,
          macros: { protein: 150, carbs: 200, fat: 67 },
          meals: [
            {
              meal: 'Café da manhã',
              time: '07:00',
              foods: ['Aveia com banana'],
              calories: 400
            }
          ]
        })
      };
    }

    // Endpoint de dashboard
    if (apiPath === '/tracking/dashboard') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          total_workouts: 15,
          current_weight: 75,
          calories_today: 1800,
          weekly_goal: 4,
          workouts_this_week: 3
        })
      };
    }

    // Endpoints de tracking (POST)
    if (apiPath.startsWith('/tracking/') && event.httpMethod === 'POST') {
      return {
        statusCode: 201,
        headers,
        body: JSON.stringify({
          message: 'Dados registrados com sucesso',
          id: Math.floor(Math.random() * 1000)
        })
      };
    }

    // Endpoints de tracking (GET)
    if (apiPath.startsWith('/tracking/')) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          data: [],
          message: 'Dados obtidos com sucesso'
        })
      };
    }

    // Endpoint não encontrado
    return {
      statusCode: 404,
      headers,
      body: JSON.stringify({
        error: 'Endpoint não encontrado',
        path: apiPath
      })
    };

  } catch (error) {
    console.error('Erro na função:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Erro interno do servidor',
        message: error.message
      })
    };
  }
};

// Updated Thu Sep  4 18:28:58 EDT 2025

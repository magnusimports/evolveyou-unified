// Cliente da API para comunicação com o backend
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:5000/api';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('auth_token');
  }

  // Configurar token de autenticação
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  // Obter headers padrão
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Fazer requisição HTTP
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Erro na requisição');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Métodos HTTP
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // ===== AUTENTICAÇÃO =====

  async register(userData) {
    const response = await this.post('/auth/register', userData);
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    return response;
  }

  async login(credentials) {
    const response = await this.post('/auth/login', credentials);
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    return response;
  }

  async getCurrentUser() {
    return this.get('/auth/me');
  }

  async completeOnboarding(profileData) {
    return this.post('/auth/onboarding', profileData);
  }

  logout() {
    this.setToken(null);
  }

  // ===== CONTEÚDO =====

  async getExercises(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.get(`/content/exercises?${params}`);
  }

  async getExercise(id) {
    return this.get(`/content/exercises/${id}`);
  }

  async getRecipes(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.get(`/content/recipes?${params}`);
  }

  async getRecipe(id) {
    return this.get(`/content/recipes/${id}`);
  }

  // ===== PLANOS =====

  async getWorkoutPlan() {
    return this.get('/plans/workout');
  }

  async getDietPlan() {
    return this.get('/plans/diet');
  }

  async getProgress() {
    return this.get('/plans/progress');
  }

  async calculateNutrition(data) {
    return this.post('/plans/nutrition-calculator', data);
  }

  // ===== TRACKING =====

  async logWorkout(workoutData) {
    return this.post('/tracking/workouts', workoutData);
  }

  async getWorkoutHistory(params = {}) {
    const queryParams = new URLSearchParams(params);
    return this.get(`/tracking/workouts?${queryParams}`);
  }

  async logMeal(mealData) {
    return this.post('/tracking/meals', mealData);
  }

  async getMealHistory(date) {
    return this.get(`/tracking/meals?date=${date}`);
  }

  async logWeight(weightData) {
    return this.post('/tracking/weight', weightData);
  }

  async getWeightHistory(limit = 30) {
    return this.get(`/tracking/weight?limit=${limit}`);
  }

  async getDashboard() {
    return this.get('/tracking/dashboard');
  }

  // ===== PROGRESSO =====

  async getMeasurements() {
    return this.get('/tracking/measurements');
  }

  async logMeasurements(measurements) {
    return this.post('/tracking/measurements', measurements);
  }

  async getProgressPhotos() {
    return this.get('/tracking/photos');
  }

  async uploadProgressPhoto(formData) {
    return this.request('/tracking/photos', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
      body: formData,
    });
  }

  async getAchievements() {
    return this.get('/tracking/achievements');
  }

  async getGoals() {
    return this.get('/tracking/goals');
  }

  async createGoal(goalData) {
    return this.post('/tracking/goals', goalData);
  }

  async updateGoal(goalId, goalData) {
    return this.put(`/tracking/goals/${goalId}`, goalData);
  }

  async deleteGoal(goalId) {
    return this.delete(`/tracking/goals/${goalId}`);
  }

  // ===== SAÚDE =====

  async healthCheck() {
    return this.get('/health');
  }
}

// Instância singleton da API
export const api = new ApiClient();
export default api;


import { 
  collection, 
  doc, 
  setDoc, 
  getDoc, 
  getDocs, 
  updateDoc, 
  deleteDoc, 
  query, 
  where, 
  orderBy, 
  limit,
  serverTimestamp 
} from 'firebase/firestore';
import { db } from '../config/firebase';

// Serviço completo de nutrição integrado com Firebase
export class NutritionService {
  
  // ==================== PLANOS ALIMENTARES ====================
  
  /**
   * Salva um plano alimentar completo no Firebase
   */
  static async saveMealPlan(userId, mealPlan, planName = null) {
    try {
      const planId = planName ? `${userId}_${planName}` : `${userId}_${Date.now()}`;
      const planRef = doc(db, 'meal_plans', planId);
      
      const planData = {
        userId,
        planName: planName || `Plano ${new Date().toLocaleDateString('pt-BR')}`,
        meals: mealPlan,
        nutritionSummary: this.calculatePlanNutrition(mealPlan),
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
        isActive: true
      };
      
      await setDoc(planRef, planData);
      return { success: true, planId, data: planData };
    } catch (error) {
      console.error('Erro ao salvar plano alimentar:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Busca todos os planos alimentares de um usuário
   */
  static async getUserMealPlans(userId) {
    try {
      const plansQuery = query(
        collection(db, 'meal_plans'),
        where('userId', '==', userId),
        orderBy('createdAt', 'desc')
      );
      
      const snapshot = await getDocs(plansQuery);
      const plans = [];
      
      snapshot.forEach((doc) => {
        plans.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return { success: true, plans };
    } catch (error) {
      console.error('Erro ao buscar planos alimentares:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Busca um plano alimentar específico
   */
  static async getMealPlan(planId) {
    try {
      const planRef = doc(db, 'meal_plans', planId);
      const planSnap = await getDoc(planRef);
      
      if (planSnap.exists()) {
        return { 
          success: true, 
          plan: { id: planSnap.id, ...planSnap.data() } 
        };
      } else {
        return { success: false, error: 'Plano não encontrado' };
      }
    } catch (error) {
      console.error('Erro ao buscar plano alimentar:', error);
      return { success: false, error: error.message };
    }
  }
  
  // ==================== REGISTRO DIÁRIO ====================
  
  /**
   * Registra o consumo de alimentos do dia
   */
  static async saveDailyIntake(userId, date, meals) {
    try {
      const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
      const intakeId = `${userId}_${dateStr}`;
      const intakeRef = doc(db, 'daily_intake', intakeId);
      
      const intakeData = {
        userId,
        date: dateStr,
        meals,
        nutritionSummary: this.calculatePlanNutrition(meals),
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      };
      
      await setDoc(intakeRef, intakeData, { merge: true });
      return { success: true, intakeId, data: intakeData };
    } catch (error) {
      console.error('Erro ao salvar consumo diário:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Busca o consumo de um dia específico
   */
  static async getDailyIntake(userId, date) {
    try {
      const dateStr = date.toISOString().split('T')[0];
      const intakeId = `${userId}_${dateStr}`;
      const intakeRef = doc(db, 'daily_intake', intakeId);
      const intakeSnap = await getDoc(intakeRef);
      
      if (intakeSnap.exists()) {
        return { 
          success: true, 
          intake: { id: intakeSnap.id, ...intakeSnap.data() } 
        };
      } else {
        // Retorna estrutura vazia se não houver dados
        return { 
          success: true, 
          intake: {
            id: intakeId,
            userId,
            date: dateStr,
            meals: {
              cafe_manha: [],
              lanche_manha: [],
              almoco: [],
              lanche_tarde: [],
              jantar: [],
              ceia: []
            },
            nutritionSummary: {
              energia_kcal: 0,
              proteina_g: 0,
              carboidrato_g: 0,
              lipidios_g: 0,
              fibra_g: 0
            }
          }
        };
      }
    } catch (error) {
      console.error('Erro ao buscar consumo diário:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Busca histórico de consumo (últimos N dias)
   */
  static async getIntakeHistory(userId, days = 7) {
    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - days);
      
      const historyQuery = query(
        collection(db, 'daily_intake'),
        where('userId', '==', userId),
        where('date', '>=', startDate.toISOString().split('T')[0]),
        where('date', '<=', endDate.toISOString().split('T')[0]),
        orderBy('date', 'desc')
      );
      
      const snapshot = await getDocs(historyQuery);
      const history = [];
      
      snapshot.forEach((doc) => {
        history.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return { success: true, history };
    } catch (error) {
      console.error('Erro ao buscar histórico:', error);
      return { success: false, error: error.message };
    }
  }
  
  // ==================== ALIMENTOS FAVORITOS ====================
  
  /**
   * Adiciona alimento aos favoritos
   */
  static async addFavoriteFood(userId, food) {
    try {
      const favoriteId = `${userId}_${food.id}`;
      const favoriteRef = doc(db, 'favorite_foods', favoriteId);
      
      const favoriteData = {
        userId,
        foodId: food.id,
        foodData: food,
        addedAt: serverTimestamp()
      };
      
      await setDoc(favoriteRef, favoriteData);
      return { success: true, favoriteId };
    } catch (error) {
      console.error('Erro ao adicionar favorito:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Remove alimento dos favoritos
   */
  static async removeFavoriteFood(userId, foodId) {
    try {
      const favoriteId = `${userId}_${foodId}`;
      const favoriteRef = doc(db, 'favorite_foods', favoriteId);
      
      await deleteDoc(favoriteRef);
      return { success: true };
    } catch (error) {
      console.error('Erro ao remover favorito:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Busca alimentos favoritos do usuário
   */
  static async getFavoriteFoods(userId) {
    try {
      const favoritesQuery = query(
        collection(db, 'favorite_foods'),
        where('userId', '==', userId),
        orderBy('addedAt', 'desc')
      );
      
      const snapshot = await getDocs(favoritesQuery);
      const favorites = [];
      
      snapshot.forEach((doc) => {
        favorites.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return { success: true, favorites };
    } catch (error) {
      console.error('Erro ao buscar favoritos:', error);
      return { success: false, error: error.message };
    }
  }
  
  // ==================== METAS NUTRICIONAIS ====================
  
  /**
   * Salva/atualiza metas nutricionais do usuário
   */
  static async saveNutritionGoals(userId, goals) {
    try {
      const goalsRef = doc(db, 'nutrition_goals', userId);
      
      const goalsData = {
        userId,
        ...goals,
        updatedAt: serverTimestamp()
      };
      
      await setDoc(goalsRef, goalsData, { merge: true });
      return { success: true, data: goalsData };
    } catch (error) {
      console.error('Erro ao salvar metas:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Busca metas nutricionais do usuário
   */
  static async getNutritionGoals(userId) {
    try {
      const goalsRef = doc(db, 'nutrition_goals', userId);
      const goalsSnap = await getDoc(goalsRef);
      
      if (goalsSnap.exists()) {
        return { 
          success: true, 
          goals: { id: goalsSnap.id, ...goalsSnap.data() } 
        };
      } else {
        return { success: false, error: 'Metas não encontradas' };
      }
    } catch (error) {
      console.error('Erro ao buscar metas:', error);
      return { success: false, error: error.message };
    }
  }
  
  // ==================== FUNÇÕES UTILITÁRIAS ====================
  
  /**
   * Calcula resumo nutricional de um plano/consumo
   */
  static calculatePlanNutrition(meals) {
    const allFoods = Object.values(meals).flat();
    
    return allFoods.reduce((total, food) => ({
      energia_kcal: total.energia_kcal + (food.energia_kcal || 0),
      proteina_g: total.proteina_g + (food.proteina_g || 0),
      carboidrato_g: total.carboidrato_g + (food.carboidrato_g || 0),
      lipidios_g: total.lipidios_g + (food.lipidios_g || 0),
      fibra_g: total.fibra_g + (food.fibra_g || 0),
      calcio_mg: total.calcio_mg + (food.calcio_mg || 0),
      ferro_mg: total.ferro_mg + (food.ferro_mg || 0),
      sodio_mg: total.sodio_mg + (food.sodio_mg || 0)
    }), {
      energia_kcal: 0,
      proteina_g: 0,
      carboidrato_g: 0,
      lipidios_g: 0,
      fibra_g: 0,
      calcio_mg: 0,
      ferro_mg: 0,
      sodio_mg: 0
    });
  }
  
  /**
   * Compara consumo com metas e retorna progresso
   */
  static calculateProgress(consumed, goals) {
    return {
      calories: {
        consumed: consumed.energia_kcal,
        goal: goals.energia_kcal,
        percentage: Math.round((consumed.energia_kcal / goals.energia_kcal) * 100)
      },
      protein: {
        consumed: consumed.proteina_g,
        goal: goals.proteina_g,
        percentage: Math.round((consumed.proteina_g / goals.proteina_g) * 100)
      },
      carbs: {
        consumed: consumed.carboidrato_g,
        goal: goals.carboidrato_g,
        percentage: Math.round((consumed.carboidrato_g / goals.carboidrato_g) * 100)
      },
      fat: {
        consumed: consumed.lipidios_g,
        goal: goals.lipidios_g,
        percentage: Math.round((consumed.lipidios_g / goals.lipidios_g) * 100)
      }
    };
  }
  
  /**
   * Gera sugestões baseadas no histórico
   */
  static generateSuggestions(history, goals) {
    // Análise do histórico para sugestões inteligentes
    const suggestions = [];
    
    if (history.length > 0) {
      const avgCalories = history.reduce((sum, day) => 
        sum + day.nutritionSummary.energia_kcal, 0) / history.length;
      
      if (avgCalories < goals.energia_kcal * 0.8) {
        suggestions.push({
          type: 'warning',
          message: 'Você está consumindo poucas calorias. Considere adicionar lanches saudáveis.',
          action: 'add_snacks'
        });
      }
      
      const avgProtein = history.reduce((sum, day) => 
        sum + day.nutritionSummary.proteina_g, 0) / history.length;
      
      if (avgProtein < goals.proteina_g * 0.8) {
        suggestions.push({
          type: 'info',
          message: 'Aumente o consumo de proteínas. Adicione ovos, frango ou leguminosas.',
          action: 'add_protein'
        });
      }
    }
    
    return suggestions;
  }
}

export default NutritionService;


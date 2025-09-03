import { useState, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';
import NutritionService from '../services/nutritionService';

/**
 * Hook personalizado para gerenciar dados de nutrição
 * Integra com Firebase e fornece estado reativo
 */
export const useNutrition = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Estados principais
  const [mealPlans, setMealPlans] = useState([]);
  const [currentDayIntake, setCurrentDayIntake] = useState(null);
  const [nutritionGoals, setNutritionGoals] = useState(null);
  const [favoriteFoods, setFavoriteFoods] = useState([]);
  const [intakeHistory, setIntakeHistory] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

  // ==================== PLANOS ALIMENTARES ====================
  
  /**
   * Carrega todos os planos alimentares do usuário
   */
  const loadMealPlans = useCallback(async () => {
    if (!user?.uid) return;
    
    setLoading(true);
    try {
      const result = await NutritionService.getUserMealPlans(user.uid);
      if (result.success) {
        setMealPlans(result.plans);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Erro ao carregar planos alimentares');
    } finally {
      setLoading(false);
    }
  }, [user?.uid]);

  /**
   * Salva um novo plano alimentar
   */
  const saveMealPlan = useCallback(async (mealPlan, planName) => {
    if (!user?.uid) return { success: false, error: 'Usuário não autenticado' };
    
    setLoading(true);
    try {
      const result = await NutritionService.saveMealPlan(user.uid, mealPlan, planName);
      if (result.success) {
        await loadMealPlans(); // Recarrega a lista
      }
      return result;
    } catch (err) {
      const error = 'Erro ao salvar plano alimentar';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, [user?.uid, loadMealPlans]);

  // ==================== CONSUMO DIÁRIO ====================
  
  /**
   * Carrega o consumo do dia atual
   */
  const loadTodayIntake = useCallback(async () => {
    if (!user?.uid) return;
    
    setLoading(true);
    try {
      const today = new Date();
      const result = await NutritionService.getDailyIntake(user.uid, today);
      if (result.success) {
        setCurrentDayIntake(result.intake);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Erro ao carregar consumo do dia');
    } finally {
      setLoading(false);
    }
  }, [user?.uid]);

  /**
   * Salva o consumo de uma refeição
   */
  const saveMealIntake = useCallback(async (mealType, foods, date = new Date()) => {
    if (!user?.uid) return { success: false, error: 'Usuário não autenticado' };
    
    setLoading(true);
    try {
      // Busca o consumo atual do dia
      const currentIntake = await NutritionService.getDailyIntake(user.uid, date);
      
      if (currentIntake.success) {
        // Atualiza apenas a refeição específica
        const updatedMeals = {
          ...currentIntake.intake.meals,
          [mealType]: foods
        };
        
        const result = await NutritionService.saveDailyIntake(user.uid, date, updatedMeals);
        
        if (result.success) {
          // Atualiza o estado local se for o dia atual
          const today = new Date().toISOString().split('T')[0];
          const targetDate = date.toISOString().split('T')[0];
          
          if (today === targetDate) {
            setCurrentDayIntake(result.data);
          }
        }
        
        return result;
      } else {
        return currentIntake;
      }
    } catch (err) {
      const error = 'Erro ao salvar refeição';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, [user?.uid]);

  /**
   * Adiciona um alimento a uma refeição
   */
  const addFoodToMeal = useCallback(async (mealType, food, date = new Date()) => {
    if (!currentDayIntake) return { success: false, error: 'Dados do dia não carregados' };
    
    const currentMealFoods = currentDayIntake.meals[mealType] || [];
    const updatedFoods = [...currentMealFoods, { ...food, addedAt: new Date().toISOString() }];
    
    return await saveMealIntake(mealType, updatedFoods, date);
  }, [currentDayIntake, saveMealIntake]);

  /**
   * Remove um alimento de uma refeição
   */
  const removeFoodFromMeal = useCallback(async (mealType, foodIndex, date = new Date()) => {
    if (!currentDayIntake) return { success: false, error: 'Dados do dia não carregados' };
    
    const currentMealFoods = currentDayIntake.meals[mealType] || [];
    const updatedFoods = currentMealFoods.filter((_, index) => index !== foodIndex);
    
    return await saveMealIntake(mealType, updatedFoods, date);
  }, [currentDayIntake, saveMealIntake]);

  // ==================== HISTÓRICO ====================
  
  /**
   * Carrega histórico de consumo
   */
  const loadIntakeHistory = useCallback(async (days = 7) => {
    if (!user?.uid) return;
    
    setLoading(true);
    try {
      const result = await NutritionService.getIntakeHistory(user.uid, days);
      if (result.success) {
        setIntakeHistory(result.history);
        
        // Gera sugestões baseadas no histórico
        if (nutritionGoals) {
          const suggestions = NutritionService.generateSuggestions(result.history, nutritionGoals);
          setSuggestions(suggestions);
        }
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Erro ao carregar histórico');
    } finally {
      setLoading(false);
    }
  }, [user?.uid, nutritionGoals]);

  // ==================== METAS NUTRICIONAIS ====================
  
  /**
   * Carrega metas nutricionais do usuário
   */
  const loadNutritionGoals = useCallback(async () => {
    if (!user?.uid) return;
    
    setLoading(true);
    try {
      const result = await NutritionService.getNutritionGoals(user.uid);
      if (result.success) {
        setNutritionGoals(result.goals);
      } else {
        // Se não há metas, pode usar dados do perfil do usuário
        console.log('Metas não encontradas, usando dados do perfil');
      }
    } catch (err) {
      setError('Erro ao carregar metas nutricionais');
    } finally {
      setLoading(false);
    }
  }, [user?.uid]);

  /**
   * Salva metas nutricionais
   */
  const saveNutritionGoals = useCallback(async (goals) => {
    if (!user?.uid) return { success: false, error: 'Usuário não autenticado' };
    
    setLoading(true);
    try {
      const result = await NutritionService.saveNutritionGoals(user.uid, goals);
      if (result.success) {
        setNutritionGoals(result.data);
      }
      return result;
    } catch (err) {
      const error = 'Erro ao salvar metas';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  }, [user?.uid]);

  // ==================== FAVORITOS ====================
  
  /**
   * Carrega alimentos favoritos
   */
  const loadFavoriteFoods = useCallback(async () => {
    if (!user?.uid) return;
    
    setLoading(true);
    try {
      const result = await NutritionService.getFavoriteFoods(user.uid);
      if (result.success) {
        setFavoriteFoods(result.favorites);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Erro ao carregar favoritos');
    } finally {
      setLoading(false);
    }
  }, [user?.uid]);

  /**
   * Adiciona alimento aos favoritos
   */
  const addFavoriteFood = useCallback(async (food) => {
    if (!user?.uid) return { success: false, error: 'Usuário não autenticado' };
    
    const result = await NutritionService.addFavoriteFood(user.uid, food);
    if (result.success) {
      await loadFavoriteFoods(); // Recarrega a lista
    }
    return result;
  }, [user?.uid, loadFavoriteFoods]);

  /**
   * Remove alimento dos favoritos
   */
  const removeFavoriteFood = useCallback(async (foodId) => {
    if (!user?.uid) return { success: false, error: 'Usuário não autenticado' };
    
    const result = await NutritionService.removeFavoriteFood(user.uid, foodId);
    if (result.success) {
      await loadFavoriteFoods(); // Recarrega a lista
    }
    return result;
  }, [user?.uid, loadFavoriteFoods]);

  // ==================== CÁLCULOS E ANÁLISES ====================
  
  /**
   * Calcula progresso nutricional do dia
   */
  const getDayProgress = useCallback(() => {
    if (!currentDayIntake || !nutritionGoals) return null;
    
    return NutritionService.calculateProgress(
      currentDayIntake.nutritionSummary,
      nutritionGoals
    );
  }, [currentDayIntake, nutritionGoals]);

  /**
   * Calcula estatísticas da semana
   */
  const getWeekStats = useCallback(() => {
    if (!intakeHistory.length || !nutritionGoals) return null;
    
    const weekData = intakeHistory.slice(0, 7);
    const avgCalories = weekData.reduce((sum, day) => 
      sum + day.nutritionSummary.energia_kcal, 0) / weekData.length;
    
    const avgProtein = weekData.reduce((sum, day) => 
      sum + day.nutritionSummary.proteina_g, 0) / weekData.length;
    
    return {
      avgCalories: Math.round(avgCalories),
      avgProtein: Math.round(avgProtein),
      goalCalories: nutritionGoals.energia_kcal,
      goalProtein: nutritionGoals.proteina_g,
      daysTracked: weekData.length,
      consistency: Math.round((weekData.length / 7) * 100)
    };
  }, [intakeHistory, nutritionGoals]);

  // ==================== EFEITOS ====================
  
  // Carrega dados iniciais quando o usuário está autenticado
  useEffect(() => {
    if (user?.uid) {
      loadTodayIntake();
      loadMealPlans();
      loadNutritionGoals();
      loadFavoriteFoods();
      loadIntakeHistory();
    }
  }, [user?.uid, loadTodayIntake, loadMealPlans, loadNutritionGoals, loadFavoriteFoods, loadIntakeHistory]);

  // Limpa dados quando o usuário faz logout
  useEffect(() => {
    if (!user) {
      setMealPlans([]);
      setCurrentDayIntake(null);
      setNutritionGoals(null);
      setFavoriteFoods([]);
      setIntakeHistory([]);
      setSuggestions([]);
      setError(null);
    }
  }, [user]);

  return {
    // Estados
    loading,
    error,
    mealPlans,
    currentDayIntake,
    nutritionGoals,
    favoriteFoods,
    intakeHistory,
    suggestions,
    
    // Ações - Planos
    saveMealPlan,
    loadMealPlans,
    
    // Ações - Consumo diário
    saveMealIntake,
    addFoodToMeal,
    removeFoodFromMeal,
    loadTodayIntake,
    
    // Ações - Histórico
    loadIntakeHistory,
    
    // Ações - Metas
    saveNutritionGoals,
    loadNutritionGoals,
    
    // Ações - Favoritos
    addFavoriteFood,
    removeFavoriteFood,
    loadFavoriteFoods,
    
    // Cálculos
    getDayProgress,
    getWeekStats,
    
    // Utilitários
    clearError: () => setError(null)
  };
};

export default useNutrition;


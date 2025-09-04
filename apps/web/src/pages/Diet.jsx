import React, { useState, useEffect } from 'react';
import { api } from '../lib/api.js';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  UtensilsCrossed, 
  Plus, 
  Target,
  Calendar,
  Flame,
  Beef,
  Wheat,
  Droplets,
  Clock,
  Search,
  CheckCircle
} from 'lucide-react';

const Diet = () => {
  const [dietPlan, setDietPlan] = useState(null);
  const [recipes, setRecipes] = useState([]);
  const [mealHistory, setMealHistory] = useState([]);
  const [todayMeals, setTodayMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('plan');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const today = new Date().toISOString().split('T')[0];
        const [planData, recipesData, todayMealsData] = await Promise.all([
          api.getDietPlan(),
          api.getRecipes(),
          api.getMealHistory(today)
        ]);
        
        setDietPlan(planData);
        setRecipes(recipesData.recipes || []);
        setTodayMeals(todayMealsData.meals || []);
      } catch (error) {
        console.error('Erro ao carregar dados de dieta:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const logMeal = async (recipe, mealType) => {
    try {
      const mealData = {
        recipe_id: recipe.id,
        meal_type: mealType,
        portions: 1
      };

      await api.logMeal(mealData);
      
      // Recarregar refeições de hoje
      const today = new Date().toISOString().split('T')[0];
      const todayMealsData = await api.getMealHistory(today);
      setTodayMeals(todayMealsData.meals || []);
    } catch (error) {
      console.error('Erro ao registrar refeição:', error);
    }
  };

  const calculateNutritionProgress = () => {
    const totalCalories = todayMeals.reduce((sum, meal) => sum + (meal.calories || 0), 0);
    const totalProtein = todayMeals.reduce((sum, meal) => sum + (meal.protein || 0), 0);
    const totalCarbs = todayMeals.reduce((sum, meal) => sum + (meal.carbs || 0), 0);
    const totalFat = todayMeals.reduce((sum, meal) => sum + (meal.fat || 0), 0);

    const targets = dietPlan?.daily_targets || {
      calories: 2000,
      protein: 150,
      carbs: 250,
      fat: 67
    };

    return {
      calories: { current: totalCalories, target: targets.calories, percentage: (totalCalories / targets.calories) * 100 },
      protein: { current: totalProtein, target: targets.protein, percentage: (totalProtein / targets.protein) * 100 },
      carbs: { current: totalCarbs, target: targets.carbs, percentage: (totalCarbs / targets.carbs) * 100 },
      fat: { current: totalFat, target: targets.fat, percentage: (totalFat / targets.fat) * 100 }
    };
  };

  const filteredRecipes = recipes.filter(recipe =>
    recipe.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    recipe.meal_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const nutrition = calculateNutritionProgress();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dieta</h1>
          <p className="text-gray-600 mt-1">
            Seu plano alimentar personalizado
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-gray-500" />
          <span className="text-sm text-gray-600">
            {new Date().toLocaleDateString('pt-BR', { 
              weekday: 'long', 
              day: 'numeric', 
              month: 'long' 
            })}
          </span>
        </div>
      </div>

      {/* Resumo Nutricional */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Calorias</CardTitle>
            <Flame className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(nutrition.calories.current)} / {nutrition.calories.target}
            </div>
            <Progress value={Math.min(nutrition.calories.percentage, 100)} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-2">
              {Math.round(nutrition.calories.percentage)}% da meta diária
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Proteína</CardTitle>
            <Beef className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(nutrition.protein.current)}g / {nutrition.protein.target}g
            </div>
            <Progress value={Math.min(nutrition.protein.percentage, 100)} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-2">
              {Math.round(nutrition.protein.percentage)}% da meta
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Carboidratos</CardTitle>
            <Wheat className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(nutrition.carbs.current)}g / {nutrition.carbs.target}g
            </div>
            <Progress value={Math.min(nutrition.carbs.percentage, 100)} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-2">
              {Math.round(nutrition.carbs.percentage)}% da meta
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Gorduras</CardTitle>
            <Droplets className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(nutrition.fat.current)}g / {nutrition.fat.target}g
            </div>
            <Progress value={Math.min(nutrition.fat.percentage, 100)} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-2">
              {Math.round(nutrition.fat.percentage)}% da meta
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="plan">Plano</TabsTrigger>
          <TabsTrigger value="recipes">Receitas</TabsTrigger>
          <TabsTrigger value="history">Hoje</TabsTrigger>
        </TabsList>

        {/* Plano Alimentar */}
        <TabsContent value="plan" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Plano Alimentar de Hoje</CardTitle>
              <CardDescription>Suas refeições planejadas para hoje</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {['cafe_da_manha', 'almoco', 'jantar', 'lanche'].map((mealType) => {
                  const mealNames = {
                    cafe_da_manha: 'Café da Manhã',
                    almoco: 'Almoço',
                    jantar: 'Jantar',
                    lanche: 'Lanche'
                  };

                  const plannedMeal = dietPlan?.meals?.find(m => m.meal_type === mealType);
                  const loggedMeal = todayMeals.find(m => m.meal_type === mealType);

                  return (
                    <div key={mealType} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold flex items-center space-x-2">
                          <UtensilsCrossed className="w-4 h-4" />
                          <span>{mealNames[mealType]}</span>
                        </h3>
                        {loggedMeal && (
                          <Badge variant="secondary">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Registrado
                          </Badge>
                        )}
                      </div>
                      
                      {plannedMeal ? (
                        <div className="space-y-2">
                          <h4 className="font-medium">{plannedMeal.name}</h4>
                          <p className="text-sm text-gray-600">{plannedMeal.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>{plannedMeal.calories} kcal</span>
                            <span>{plannedMeal.protein}g proteína</span>
                            <span>{plannedMeal.prep_time}min preparo</span>
                          </div>
                          {!loggedMeal && (
                            <Button 
                              size="sm" 
                              onClick={() => logMeal(plannedMeal, mealType)}
                              className="mt-2"
                            >
                              Registrar Refeição
                            </Button>
                          )}
                        </div>
                      ) : (
                        <div className="text-center py-4">
                          <p className="text-gray-500 text-sm">Nenhuma refeição planejada</p>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            onClick={() => setActiveTab('recipes')}
                            className="mt-2"
                          >
                            <Plus className="w-3 h-3 mr-1" />
                            Adicionar Receita
                          </Button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Receitas */}
        <TabsContent value="recipes" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Receitas Disponíveis</CardTitle>
              <CardDescription>Explore nossa biblioteca de receitas saudáveis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="Buscar receitas..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredRecipes.map((recipe) => (
                    <Card key={recipe.id} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <Badge variant="outline" className="capitalize">
                            {recipe.meal_type.replace('_', ' ')}
                          </Badge>
                          <Badge variant="secondary">
                            <Clock className="w-3 h-3 mr-1" />
                            {recipe.prep_time}min
                          </Badge>
                        </div>
                        <CardTitle className="text-lg">{recipe.name}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-600 mb-3">{recipe.description}</p>
                        
                        <div className="grid grid-cols-2 gap-2 text-xs text-gray-500 mb-3">
                          <span>{recipe.calories} kcal</span>
                          <span>{recipe.protein}g proteína</span>
                          <span>{recipe.carbs}g carbs</span>
                          <span>{recipe.fat}g gordura</span>
                        </div>

                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="flex-1"
                          >
                            Ver Receita
                          </Button>
                          <Button 
                            size="sm" 
                            onClick={() => logMeal(recipe, recipe.meal_type)}
                            className="flex-1"
                          >
                            <Plus className="w-3 h-3 mr-1" />
                            Adicionar
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Histórico de Hoje */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Refeições de Hoje</CardTitle>
              <CardDescription>Suas refeições registradas hoje</CardDescription>
            </CardHeader>
            <CardContent>
              {todayMeals.length > 0 ? (
                <div className="space-y-3">
                  {todayMeals.map((meal, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                          <UtensilsCrossed className="w-5 h-5 text-green-600" />
                        </div>
                        <div>
                          <h3 className="font-medium">{meal.name}</h3>
                          <p className="text-sm text-gray-600 capitalize">
                            {meal.meal_type.replace('_', ' ')} • {meal.portions} porção(ões)
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{meal.calories} kcal</p>
                        <p className="text-xs text-gray-500">{meal.protein}g proteína</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <UtensilsCrossed className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">
                    Nenhuma refeição registrada
                  </h3>
                  <p className="text-gray-500 mb-4">
                    Registre suas refeições para acompanhar sua nutrição
                  </p>
                  <Button onClick={() => setActiveTab('plan')}>
                    Ver Plano Alimentar
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Diet;


import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Utensils, 
  Target, 
  Clock, 
  Plus,
  Apple,
  Beef,
  Wheat,
  Droplets,
  TrendingUp,
  Calendar,
  CheckCircle
} from 'lucide-react';

const NutritionTab = ({ userProfile }) => {
  const [selectedMeal, setSelectedMeal] = useState('breakfast');
  
  const calculations = userProfile.calculations || {};
  const anamneseAnswers = userProfile.anamneseAnswers || {};
  const personalInfo = anamneseAnswers.personal_info || {};
  
  // Dados simulados para demonstração
  const todayIntake = {
    calories: 1850,
    protein: 95,
    carbs: 180,
    fat: 65,
    water: 2.2
  };

  const targetIntake = {
    calories: calculations.targetCalories || 2000,
    protein: calculations.macros?.protein.grams || 120,
    carbs: calculations.macros?.carbs.grams || 200,
    fat: calculations.macros?.fat.grams || 70,
    water: Math.round((parseFloat(personalInfo.weight) || 70) * 35 / 1000 * 10) / 10
  };

  const meals = {
    breakfast: {
      name: 'Café da Manhã',
      time: '08:00',
      calories: 450,
      foods: [
        { name: '2 ovos mexidos', calories: 140, protein: 12, carbs: 2, fat: 10 },
        { name: '2 fatias de pão integral', calories: 160, protein: 6, carbs: 30, fat: 2 },
        { name: '1 banana média', calories: 105, protein: 1, carbs: 27, fat: 0 },
        { name: '1 xícara de café com leite', calories: 45, protein: 2, carbs: 6, fat: 2 }
      ]
    },
    lunch: {
      name: 'Almoço',
      time: '12:30',
      calories: 650,
      foods: [
        { name: '150g peito de frango grelhado', calories: 250, protein: 46, carbs: 0, fat: 6 },
        { name: '1 xícara de arroz integral', calories: 220, protein: 5, carbs: 45, fat: 2 },
        { name: '1/2 xícara de feijão', calories: 120, protein: 8, carbs: 20, fat: 1 },
        { name: 'Salada verde com azeite', calories: 60, protein: 2, carbs: 8, fat: 3 }
      ]
    },
    snack: {
      name: 'Lanche',
      time: '15:30',
      calories: 250,
      foods: [
        { name: '1 iogurte grego natural', calories: 130, protein: 15, carbs: 9, fat: 5 },
        { name: '30g de granola', calories: 120, protein: 3, carbs: 18, fat: 4 }
      ]
    },
    dinner: {
      name: 'Jantar',
      time: '19:00',
      calories: 500,
      foods: [
        { name: '120g salmão grelhado', calories: 280, protein: 39, carbs: 0, fat: 13 },
        { name: '200g batata doce assada', calories: 180, protein: 4, carbs: 41, fat: 0 },
        { name: 'Brócolis refogado', calories: 40, protein: 4, carbs: 8, fat: 0 }
      ]
    }
  };

  const weeklyProgress = [
    { day: 'Seg', calories: 1950, target: 2000, percentage: 97 },
    { day: 'Ter', calories: 2100, target: 2000, percentage: 105 },
    { day: 'Qua', calories: 1800, target: 2000, percentage: 90 },
    { day: 'Qui', calories: 2050, target: 2000, percentage: 102 },
    { day: 'Sex', calories: 1900, target: 2000, percentage: 95 },
    { day: 'Sáb', calories: 2200, target: 2000, percentage: 110 },
    { day: 'Dom', calories: 1850, target: 2000, percentage: 92 }
  ];

  const calculatePercentage = (current, target) => {
    return Math.min(Math.round((current / target) * 100), 100);
  };

  const getMacroColor = (macro) => {
    switch (macro) {
      case 'protein': return 'text-blue-600';
      case 'carbs': return 'text-green-600';
      case 'fat': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Resumo Diário */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Calorias</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayIntake.calories}</div>
            <p className="text-xs text-muted-foreground">
              Meta: {targetIntake.calories} kcal
            </p>
            <Progress 
              value={calculatePercentage(todayIntake.calories, targetIntake.calories)} 
              className="mt-2" 
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Proteína</CardTitle>
            <Beef className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{todayIntake.protein}g</div>
            <p className="text-xs text-muted-foreground">
              Meta: {targetIntake.protein}g
            </p>
            <Progress 
              value={calculatePercentage(todayIntake.protein, targetIntake.protein)} 
              className="mt-2" 
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Carboidratos</CardTitle>
            <Wheat className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{todayIntake.carbs}g</div>
            <p className="text-xs text-muted-foreground">
              Meta: {targetIntake.carbs}g
            </p>
            <Progress 
              value={calculatePercentage(todayIntake.carbs, targetIntake.carbs)} 
              className="mt-2" 
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Gorduras</CardTitle>
            <Apple className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{todayIntake.fat}g</div>
            <p className="text-xs text-muted-foreground">
              Meta: {targetIntake.fat}g
            </p>
            <Progress 
              value={calculatePercentage(todayIntake.fat, targetIntake.fat)} 
              className="mt-2" 
            />
          </CardContent>
        </Card>
      </div>

      {/* Hidratação */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Droplets className="h-5 w-5 text-blue-500" />
            Hidratação
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl font-bold text-blue-500">{todayIntake.water}L</span>
            <span className="text-sm text-muted-foreground">Meta: {targetIntake.water}L</span>
          </div>
          <Progress 
            value={calculatePercentage(todayIntake.water * 1000, targetIntake.water * 1000)} 
            className="mb-4" 
          />
          <div className="flex gap-2">
            {Array.from({ length: 8 }, (_, i) => (
              <div
                key={i}
                className={`w-8 h-10 rounded border-2 ${
                  i < Math.floor(todayIntake.water * 4) 
                    ? 'bg-blue-500 border-blue-500' 
                    : 'border-gray-300'
                }`}
              />
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Cada copo representa ~250ml
          </p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Refeições de Hoje */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Utensils className="h-5 w-5" />
              Refeições de Hoje
            </CardTitle>
            <CardDescription>
              Acompanhe suas refeições e macronutrientes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={selectedMeal} onValueChange={setSelectedMeal}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="breakfast" className="text-xs">Café</TabsTrigger>
                <TabsTrigger value="lunch" className="text-xs">Almoço</TabsTrigger>
                <TabsTrigger value="snack" className="text-xs">Lanche</TabsTrigger>
                <TabsTrigger value="dinner" className="text-xs">Jantar</TabsTrigger>
              </TabsList>

              {Object.entries(meals).map(([key, meal]) => (
                <TabsContent key={key} value={key} className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">{meal.name}</h3>
                      <p className="text-sm text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {meal.time}
                      </p>
                    </div>
                    <Badge variant="outline">
                      {meal.calories} kcal
                    </Badge>
                  </div>

                  <div className="space-y-2">
                    {meal.foods.map((food, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                        <div className="flex-1">
                          <p className="text-sm font-medium">{food.name}</p>
                          <p className="text-xs text-muted-foreground">
                            P: {food.protein}g • C: {food.carbs}g • G: {food.fat}g
                          </p>
                        </div>
                        <span className="text-sm font-medium">{food.calories} kcal</span>
                      </div>
                    ))}
                  </div>

                  <Button variant="outline" className="w-full">
                    <Plus className="h-4 w-4 mr-2" />
                    Adicionar Alimento
                  </Button>
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>

        {/* Progresso Semanal */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Progresso Semanal
            </CardTitle>
            <CardDescription>
              Consistência na meta calórica
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {weeklyProgress.map((day, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{day.day}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm">{day.calories} kcal</span>
                      {day.percentage >= 90 && day.percentage <= 110 && (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      )}
                    </div>
                  </div>
                  <Progress 
                    value={Math.min(day.percentage, 100)} 
                    className={`h-2 ${
                      day.percentage < 90 ? '[&>div]:bg-red-500' :
                      day.percentage > 110 ? '[&>div]:bg-yellow-500' :
                      '[&>div]:bg-green-500'
                    }`}
                  />
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t">
              <div className="flex items-center justify-between text-sm">
                <span>Média semanal:</span>
                <span className="font-medium">1979 kcal</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span>Consistência:</span>
                <span className="font-medium text-green-600">85%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Dicas Personalizadas */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Dicas Personalizadas
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">💪 Proteína</h4>
              <p className="text-sm text-blue-800">
                Você está {todayIntake.protein >= targetIntake.protein ? 'atingindo' : 'abaixo da'} sua meta de proteína. 
                {todayIntake.protein < targetIntake.protein && ' Tente adicionar um shake de whey ou mais ovos.'}
              </p>
            </div>
            
            <div className="p-4 bg-green-50 rounded-lg">
              <h4 className="font-medium text-green-900 mb-2">🥬 Vegetais</h4>
              <p className="text-sm text-green-800">
                Inclua mais vegetais coloridos para aumentar vitaminas e fibras. 
                Tente preencher metade do prato com vegetais.
              </p>
            </div>
            
            <div className="p-4 bg-yellow-50 rounded-lg">
              <h4 className="font-medium text-yellow-900 mb-2">⏰ Timing</h4>
              <p className="text-sm text-yellow-800">
                Baseado no seu objetivo de {
                  anamneseAnswers.primary_goal === 'weight_loss' ? 'perda de peso' :
                  anamneseAnswers.primary_goal === 'muscle_gain' ? 'ganho de massa' :
                  'manutenção'
                }, mantenha refeições regulares a cada 3-4 horas.
              </p>
            </div>
            
            <div className="p-4 bg-purple-50 rounded-lg">
              <h4 className="font-medium text-purple-900 mb-2">💧 Hidratação</h4>
              <p className="text-sm text-purple-800">
                {todayIntake.water >= targetIntake.water 
                  ? 'Parabéns! Você está bem hidratado hoje.' 
                  : `Faltam ${(targetIntake.water - todayIntake.water).toFixed(1)}L para sua meta.`
                }
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NutritionTab;


import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Dumbbell, 
  UtensilsCrossed, 
  TrendingUp, 
  Target,
  Calendar,
  Clock,
  Flame,
  Activity
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const data = await api.getDashboard();
        setDashboardData(data);
      } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const progress = dashboardData?.today_progress;
  const caloriesProgress = progress ? (progress.calories_consumed / progress.calories_target) * 100 : 0;
  const proteinProgress = progress ? (progress.protein_consumed / progress.protein_target) * 100 : 0;

  // Dados mockados para o gráfico de peso (caso não tenha dados reais)
  const weightData = dashboardData?.weight_trend?.length > 0 
    ? dashboardData.weight_trend.map(w => ({
        date: new Date(w.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
        weight: w.weight
      }))
    : [
        { date: '01/09', weight: 70 },
        { date: '02/09', weight: 69.8 },
        { date: '03/09', weight: 69.5 },
        { date: '04/09', weight: 69.3 },
      ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Olá, {user?.name?.split(' ')[0] || 'Usuário'}! 👋
          </h1>
          <p className="text-gray-600 mt-1">
            Vamos continuar sua jornada fitness hoje
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-gray-500" />
          <span className="text-sm text-gray-600">
            {new Date().toLocaleDateString('pt-BR', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </span>
        </div>
      </div>

      {/* Cards de Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Calorias */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Calorias</CardTitle>
            <Flame className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {progress?.calories_consumed || 0} / {progress?.calories_target || 2000}
            </div>
            <Progress value={caloriesProgress} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-2">
              {Math.round(caloriesProgress)}% da meta diária
            </p>
          </CardContent>
        </Card>

        {/* Proteína */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Proteína</CardTitle>
            <Target className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {progress?.protein_consumed || 0}g / {progress?.protein_target || 150}g
            </div>
            <Progress value={proteinProgress} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-2">
              {Math.round(proteinProgress)}% da meta diária
            </p>
          </CardContent>
        </Card>

        {/* Treinos da Semana */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Treinos</CardTitle>
            <Dumbbell className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardData?.weekly_workouts || 0} / 3
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Treinos esta semana
            </p>
            <Badge variant="secondary" className="mt-2">
              {progress?.workout_completed ? 'Concluído hoje' : 'Pendente hoje'}
            </Badge>
          </CardContent>
        </Card>

        {/* Refeições */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Refeições</CardTitle>
            <UtensilsCrossed className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardData?.today_meals || 0} / 3
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Refeições registradas hoje
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Seção Principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Treino do Dia */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Dumbbell className="w-5 h-5" />
              <span>Treino de Hoje</span>
            </CardTitle>
            <CardDescription>
              Seu treino planejado para hoje
            </CardDescription>
          </CardHeader>
          <CardContent>
            {progress?.workout_completed ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Dumbbell className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-green-600 mb-2">
                  Treino Concluído! 🎉
                </h3>
                <p className="text-gray-600">
                  Parabéns! Você completou seu treino de hoje.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Treino Peito e Tríceps</h3>
                  <Badge>45 min</Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Flexão de Braço</span>
                    <span className="text-gray-500">3x12</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Supino Inclinado</span>
                    <span className="text-gray-500">3x10</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Tríceps Testa</span>
                    <span className="text-gray-500">3x12</span>
                  </div>
                </div>
                <Button className="w-full mt-4">
                  <Clock className="w-4 h-4 mr-2" />
                  Iniciar Treino
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Progresso de Peso */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5" />
              <span>Progresso</span>
            </CardTitle>
            <CardDescription>
              Evolução do seu peso
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-2xl font-bold">
                  {weightData[weightData.length - 1]?.weight || 70}kg
                </div>
                <p className="text-sm text-gray-600">Peso atual</p>
              </div>
              
              <div className="h-32">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weightData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" fontSize={12} />
                    <YAxis fontSize={12} />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="weight" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              
              <Button variant="outline" className="w-full">
                Registrar Peso
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Próxima Refeição */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <UtensilsCrossed className="w-5 h-5" />
            <span>Próxima Refeição</span>
          </CardTitle>
          <CardDescription>
            Sua próxima refeição planejada
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <UtensilsCrossed className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold">Almoço - Frango Grelhado</h3>
                <p className="text-sm text-gray-600">
                  400 kcal • 35g proteína • 30g carbs
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium">12:30</p>
              <Button size="sm" className="mt-2">
                Ver Receita
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;


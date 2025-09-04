import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Activity, 
  TrendingUp, 
  Target,
  Droplets,
  Scale,
  Calculator,
  MessageCircle,
  Settings,
  LogOut,
  User,
  Utensils,
  Dumbbell,
  Brain
} from 'lucide-react';
import { useAuth } from '../hooks/useFirebaseAuth.jsx';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import CoachEVO from '../components/dashboard/CoachEVO';
import NutritionTab from '../components/dashboard/NutritionTab';
import WorkoutTab from '../components/dashboard/WorkoutTab';

const DashboardPage = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);

  // Dados do usuário (calculados durante o onboarding)
  const userProfile = user?.profile || {};
  const calculations = userProfile.calculations || {};
  const anamneseAnswers = userProfile.anamneseAnswers || {};

  useEffect(() => {
    // Simular carregamento de dados
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  // Se o usuário não completou o onboarding, mostrar mensagem
  if (!userProfile.onboardingCompleted) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle>Complete seu perfil</CardTitle>
            <CardDescription>
              Você precisa completar o processo de onboarding para acessar o dashboard.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => window.location.href = '/onboarding'} className="w-full">
              Completar perfil
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const personalInfo = anamneseAnswers.personal_info || {};
  const currentWeight = parseFloat(personalInfo.weight) || 0;
  const targetWeight = parseFloat(anamneseAnswers.target_weight?.target_weight) || currentWeight;
  const height = parseFloat(personalInfo.height) || 0;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
                <span className="text-white text-lg font-bold">E</span>
              </div>
              <div>
                <h1 className="text-xl font-bold">EvolveYou</h1>
                <p className="text-sm text-muted-foreground">
                  Olá, {user?.name || user?.email?.split('@')[0] || 'Usuário'}!
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="gap-1">
                <Activity className="h-3 w-3" />
                Online
              </Badge>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Target className="h-4 w-4" />
              Visão Geral
            </TabsTrigger>
            <TabsTrigger value="nutrition" className="flex items-center gap-2">
              <Utensils className="h-4 w-4" />
              Nutrição
            </TabsTrigger>
            <TabsTrigger value="workout" className="flex items-center gap-2">
              <Dumbbell className="h-4 w-4" />
              Treino
            </TabsTrigger>
            <TabsTrigger value="coach" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Coach EVO
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Cards de Métricas Principais */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Peso Atual</CardTitle>
                  <Scale className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{currentWeight}kg</div>
                  <p className="text-xs text-muted-foreground">
                    Meta: {targetWeight}kg
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">IMC</CardTitle>
                  <Calculator className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{calculations.bmi || 'N/A'}</div>
                  <p className={`text-xs ${calculations.bmiClassification?.color || 'text-muted-foreground'}`}>
                    {calculations.bmiClassification?.category || 'Não calculado'}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Calorias Hoje</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">2100</div>
                  <p className="text-xs text-muted-foreground">
                    Meta: {calculations.targetCalories || 2000} kcal
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Água</CardTitle>
                  <Droplets className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">2.2L</div>
                  <p className="text-xs text-muted-foreground">
                    Meta: 2.5L
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Progresso Semanal */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Progresso Semanal
                </CardTitle>
                <CardDescription>
                  Seu desempenho nos últimos 7 dias
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Treinos Concluídos</span>
                    <span className="font-medium">12/15</span>
                  </div>
                  <Progress value={80} />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Meta de Água</span>
                    <span className="font-medium">7/7 dias</span>
                  </div>
                  <Progress value={100} />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Consistência Nutricional</span>
                    <span className="font-medium">5/7 dias</span>
                  </div>
                  <Progress value={71} />
                </div>
              </CardContent>
            </Card>

            {/* Seu Perfil */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Seu Perfil
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Idade:</span> {personalInfo.age || 'N/A'} anos
                  </div>
                  <div>
                    <span className="font-medium">Altura:</span> {height || 'N/A'} cm
                  </div>
                  <div>
                    <span className="font-medium">Objetivo:</span> {
                      anamneseAnswers.primary_goal === 'weight_loss' ? 'Perder Peso' :
                      anamneseAnswers.primary_goal === 'muscle_gain' ? 'Ganhar Massa' :
                      anamneseAnswers.primary_goal === 'maintenance' ? 'Manter Peso' :
                      anamneseAnswers.primary_goal === 'performance' ? 'Performance' : 'N/A'
                    }
                  </div>
                  <div>
                    <span className="font-medium">Nível de Atividade:</span> {
                      anamneseAnswers.activity_level === 'sedentary' ? 'Sedentário' :
                      anamneseAnswers.activity_level === 'light' ? 'Levemente Ativo' :
                      anamneseAnswers.activity_level === 'moderate' ? 'Moderadamente Ativo' :
                      anamneseAnswers.activity_level === 'very_active' ? 'Muito Ativo' :
                      anamneseAnswers.activity_level === 'extremely_active' ? 'Extremamente Ativo' : 'N/A'
                    }
                  </div>
                </div>
                
                {calculations.macros && (
                  <div className="mt-4 pt-4 border-t">
                    <h4 className="font-medium mb-2">Distribuição de Macronutrientes</h4>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div className="text-center">
                        <div className="font-medium text-blue-600">{calculations.macros.protein.grams}g</div>
                        <div className="text-muted-foreground">Proteína</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-green-600">{calculations.macros.carbs.grams}g</div>
                        <div className="text-muted-foreground">Carboidratos</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-yellow-600">{calculations.macros.fat.grams}g</div>
                        <div className="text-muted-foreground">Gorduras</div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="nutrition">
            <NutritionTab userProfile={userProfile} />
          </TabsContent>

          <TabsContent value="workout">
            <WorkoutTab userProfile={userProfile} />
          </TabsContent>

          <TabsContent value="coach">
            <CoachEVO userProfile={userProfile} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default DashboardPage;


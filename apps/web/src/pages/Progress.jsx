import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress as ProgressBar } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Camera, 
  TrendingUp, 
  Target,
  Calendar,
  Award,
  Ruler,
  Scale,
  BarChart3,
  Upload,
  Download,
  Trophy,
  Star,
  Zap
} from 'lucide-react';

const Progress = () => {
  const [progressData, setProgressData] = useState({
    weight: [],
    measurements: [],
    photos: [],
    achievements: [],
    goals: []
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [newWeight, setNewWeight] = useState('');
  const [newMeasurements, setNewMeasurements] = useState({
    chest: '',
    waist: '',
    hips: '',
    bicep: '',
    thigh: ''
  });

  useEffect(() => {
    const fetchProgressData = async () => {
      try {
        const [weightData, measurementsData, photosData, achievementsData, goalsData] = await Promise.all([
          api.getWeightHistory(),
          api.getMeasurements(),
          api.getProgressPhotos(),
          api.getAchievements(),
          api.getGoals()
        ]);
        
        setProgressData({
          weight: weightData.weights || [],
          measurements: measurementsData.measurements || [],
          photos: photosData.photos || [],
          achievements: achievementsData.achievements || [],
          goals: goalsData.goals || []
        });
      } catch (error) {
        console.error('Erro ao carregar dados de progresso:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProgressData();
  }, []);

  const logWeight = async () => {
    if (!newWeight) return;
    
    try {
      await api.logWeight({ weight: parseFloat(newWeight) });
      setNewWeight('');
      // Recarregar dados
      const weightData = await api.getWeightHistory();
      setProgressData(prev => ({ ...prev, weight: weightData.weights || [] }));
    } catch (error) {
      console.error('Erro ao registrar peso:', error);
    }
  };

  const logMeasurements = async () => {
    try {
      const measurements = Object.entries(newMeasurements)
        .filter(([_, value]) => value !== '')
        .reduce((acc, [key, value]) => ({ ...acc, [key]: parseFloat(value) }), {});
      
      if (Object.keys(measurements).length === 0) return;
      
      await api.logMeasurements(measurements);
      setNewMeasurements({ chest: '', waist: '', hips: '', bicep: '', thigh: '' });
      
      // Recarregar dados
      const measurementsData = await api.getMeasurements();
      setProgressData(prev => ({ ...prev, measurements: measurementsData.measurements || [] }));
    } catch (error) {
      console.error('Erro ao registrar medidas:', error);
    }
  };

  const uploadPhoto = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
      const formData = new FormData();
      formData.append('photo', file);
      formData.append('type', 'progress');
      
      await api.uploadProgressPhoto(formData);
      
      // Recarregar fotos
      const photosData = await api.getProgressPhotos();
      setProgressData(prev => ({ ...prev, photos: photosData.photos || [] }));
    } catch (error) {
      console.error('Erro ao fazer upload da foto:', error);
    }
  };

  const calculateBMI = () => {
    if (progressData.weight.length === 0) return null;
    const latestWeight = progressData.weight[progressData.weight.length - 1];
    // Assumindo altura de 1.75m para exemplo - deveria vir do perfil do usuário
    const height = 1.75;
    return (latestWeight.weight / (height * height)).toFixed(1);
  };

  const getWeightTrend = () => {
    if (progressData.weight.length < 2) return null;
    const recent = progressData.weight.slice(-2);
    const diff = recent[1].weight - recent[0].weight;
    return diff;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const bmi = calculateBMI();
  const weightTrend = getWeightTrend();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Progresso</h1>
          <p className="text-gray-600 mt-1">
            Acompanhe sua evolução e conquistas
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

      {/* Resumo Geral */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Peso Atual</CardTitle>
            <Scale className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {progressData.weight.length > 0 
                ? `${progressData.weight[progressData.weight.length - 1].weight}kg`
                : 'N/A'
              }
            </div>
            {weightTrend !== null && (
              <p className={`text-xs ${weightTrend >= 0 ? 'text-green-600' : 'text-red-600'} mt-1`}>
                {weightTrend >= 0 ? '+' : ''}{weightTrend.toFixed(1)}kg esta semana
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">IMC</CardTitle>
            <BarChart3 className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {bmi || 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {bmi && (
                bmi < 18.5 ? 'Abaixo do peso' :
                bmi < 25 ? 'Peso normal' :
                bmi < 30 ? 'Sobrepeso' : 'Obesidade'
              )}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conquistas</CardTitle>
            <Trophy className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{progressData.achievements.length}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Badges conquistados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fotos</CardTitle>
            <Camera className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{progressData.photos.length}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Fotos de progresso
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="weight">Peso</TabsTrigger>
          <TabsTrigger value="measurements">Medidas</TabsTrigger>
          <TabsTrigger value="photos">Fotos</TabsTrigger>
          <TabsTrigger value="achievements">Conquistas</TabsTrigger>
        </TabsList>

        {/* Visão Geral */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="w-5 h-5" />
                  <span>Evolução do Peso</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {progressData.weight.length > 0 ? (
                  <div className="space-y-2">
                    {progressData.weight.slice(-5).map((entry, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">
                          {new Date(entry.date).toLocaleDateString('pt-BR')}
                        </span>
                        <span className="font-medium">{entry.weight}kg</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    Nenhum registro de peso ainda
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="w-5 h-5" />
                  <span>Metas Ativas</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {progressData.goals.length > 0 ? (
                  <div className="space-y-3">
                    {progressData.goals.slice(0, 3).map((goal, index) => (
                      <div key={index} className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">{goal.title}</span>
                          <span className="text-xs text-gray-500">
                            {Math.round(goal.progress)}%
                          </span>
                        </div>
                        <ProgressBar value={goal.progress} className="h-2" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    Nenhuma meta definida ainda
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Peso */}
        <TabsContent value="weight" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Registrar Peso</CardTitle>
              <CardDescription>Acompanhe sua evolução de peso ao longo do tempo</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2">
                <div className="flex-1">
                  <Label htmlFor="weight">Peso (kg)</Label>
                  <Input
                    id="weight"
                    type="number"
                    step="0.1"
                    placeholder="70.5"
                    value={newWeight}
                    onChange={(e) => setNewWeight(e.target.value)}
                  />
                </div>
                <Button onClick={logWeight} className="mt-6">
                  Registrar
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Histórico de Peso</CardTitle>
            </CardHeader>
            <CardContent>
              {progressData.weight.length > 0 ? (
                <div className="space-y-2">
                  {progressData.weight.map((entry, index) => (
                    <div key={index} className="flex justify-between items-center p-2 border rounded">
                      <span>{new Date(entry.date).toLocaleDateString('pt-BR')}</span>
                      <span className="font-medium">{entry.weight}kg</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Nenhum registro de peso ainda
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Medidas */}
        <TabsContent value="measurements" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Registrar Medidas</CardTitle>
              <CardDescription>Acompanhe as medidas do seu corpo</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {Object.entries(newMeasurements).map(([key, value]) => (
                  <div key={key}>
                    <Label htmlFor={key} className="capitalize">
                      {key === 'chest' ? 'Peito' :
                       key === 'waist' ? 'Cintura' :
                       key === 'hips' ? 'Quadril' :
                       key === 'bicep' ? 'Bíceps' :
                       key === 'thigh' ? 'Coxa' : key} (cm)
                    </Label>
                    <Input
                      id={key}
                      type="number"
                      step="0.1"
                      placeholder="0.0"
                      value={value}
                      onChange={(e) => setNewMeasurements(prev => ({
                        ...prev,
                        [key]: e.target.value
                      }))}
                    />
                  </div>
                ))}
              </div>
              <Button onClick={logMeasurements} className="mt-4 w-full">
                Registrar Medidas
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Fotos */}
        <TabsContent value="photos" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Fotos de Progresso</CardTitle>
              <CardDescription>Documente sua transformação visual</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">Adicione uma nova foto de progresso</p>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={uploadPhoto}
                    className="hidden"
                    id="photo-upload"
                  />
                  <Button asChild>
                    <label htmlFor="photo-upload" className="cursor-pointer">
                      <Upload className="w-4 h-4 mr-2" />
                      Fazer Upload
                    </label>
                  </Button>
                </div>

                {progressData.photos.length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {progressData.photos.map((photo, index) => (
                      <div key={index} className="relative">
                        <img
                          src={photo.url}
                          alt={`Progresso ${index + 1}`}
                          className="w-full h-32 object-cover rounded-lg"
                        />
                        <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                          {new Date(photo.date).toLocaleDateString('pt-BR')}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Conquistas */}
        <TabsContent value="achievements" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Award className="w-5 h-5" />
                <span>Suas Conquistas</span>
              </CardTitle>
              <CardDescription>Badges e marcos alcançados</CardDescription>
            </CardHeader>
            <CardContent>
              {progressData.achievements.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {progressData.achievements.map((achievement, index) => (
                    <div key={index} className="text-center p-4 border rounded-lg">
                      <div className="w-16 h-16 mx-auto mb-2 bg-yellow-100 rounded-full flex items-center justify-center">
                        <Trophy className="w-8 h-8 text-yellow-600" />
                      </div>
                      <h3 className="font-medium text-sm">{achievement.title}</h3>
                      <p className="text-xs text-gray-500 mt-1">{achievement.description}</p>
                      <Badge variant="secondary" className="mt-2">
                        {new Date(achievement.date).toLocaleDateString('pt-BR')}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Trophy className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-600 mb-2">
                    Nenhuma conquista ainda
                  </h3>
                  <p className="text-gray-500">
                    Continue treinando para desbloquear suas primeiras conquistas!
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Progress;


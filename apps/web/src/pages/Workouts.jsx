import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Dumbbell, 
  Clock, 
  Target, 
  Play, 
  Pause, 
  RotateCcw,
  Plus,
  Calendar,
  TrendingUp,
  CheckCircle
} from 'lucide-react';

const Workouts = () => {
  const [workoutPlan, setWorkoutPlan] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [currentWorkout, setCurrentWorkout] = useState(null);
  const [workoutHistory, setWorkoutHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('plan');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [planData, exercisesData, historyData] = await Promise.all([
          api.getWorkoutPlan(),
          api.getExercises(),
          api.getWorkoutHistory({ limit: 10 })
        ]);
        
        setWorkoutPlan(planData);
        setExercises(exercisesData.exercises || []);
        setWorkoutHistory(historyData.workouts || []);
      } catch (error) {
        console.error('Erro ao carregar dados de treino:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const startWorkout = (workout) => {
    setCurrentWorkout({
      ...workout,
      startTime: new Date(),
      currentExercise: 0,
      exercises: workout.exercises.map(ex => ({
        ...ex,
        sets: ex.sets.map(set => ({ ...set, completed: false }))
      }))
    });
    setActiveTab('active');
  };

  const completeSet = (exerciseIndex, setIndex) => {
    setCurrentWorkout(prev => ({
      ...prev,
      exercises: prev.exercises.map((ex, exIdx) => 
        exIdx === exerciseIndex 
          ? {
              ...ex,
              sets: ex.sets.map((set, setIdx) => 
                setIdx === setIndex ? { ...set, completed: true } : set
              )
            }
          : ex
      )
    }));
  };

  const finishWorkout = async () => {
    if (!currentWorkout) return;

    try {
      const workoutData = {
        name: currentWorkout.name,
        duration: Math.round((new Date() - currentWorkout.startTime) / 1000 / 60),
        exercises: currentWorkout.exercises.map(ex => ({
          exercise_id: ex.id,
          sets: ex.sets.map(set => ({
            reps: set.reps,
            weight: set.weight || 0,
            completed: set.completed
          }))
        }))
      };

      await api.logWorkout(workoutData);
      setCurrentWorkout(null);
      setActiveTab('plan');
      
      // Recarregar histórico
      const historyData = await api.getWorkoutHistory({ limit: 10 });
      setWorkoutHistory(historyData.workouts || []);
    } catch (error) {
      console.error('Erro ao finalizar treino:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const todayWorkout = workoutPlan?.workouts?.find(w => 
    new Date(w.date).toDateString() === new Date().toDateString()
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Treinos</h1>
          <p className="text-gray-600 mt-1">
            Seus treinos personalizados e progresso
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

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="plan">Plano</TabsTrigger>
          <TabsTrigger value="active">Treino Ativo</TabsTrigger>
          <TabsTrigger value="history">Histórico</TabsTrigger>
        </TabsList>

        {/* Plano de Treinos */}
        <TabsContent value="plan" className="space-y-6">
          {/* Treino de Hoje */}
          {todayWorkout && (
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center space-x-2">
                      <Target className="w-5 h-5 text-blue-600" />
                      <span>Treino de Hoje</span>
                    </CardTitle>
                    <CardDescription>{todayWorkout.name}</CardDescription>
                  </div>
                  <Badge variant="secondary">
                    <Clock className="w-3 h-3 mr-1" />
                    {todayWorkout.duration}min
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Exercícios</span>
                      <p className="font-semibold">{todayWorkout.exercises?.length || 0}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Séries</span>
                      <p className="font-semibold">
                        {todayWorkout.exercises?.reduce((acc, ex) => acc + (ex.sets?.length || 0), 0) || 0}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-600">Grupo</span>
                      <p className="font-semibold">{todayWorkout.muscle_group || 'Geral'}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Dificuldade</span>
                      <p className="font-semibold capitalize">{todayWorkout.difficulty || 'Intermediário'}</p>
                    </div>
                  </div>
                  
                  <Button 
                    onClick={() => startWorkout(todayWorkout)}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Iniciar Treino
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Plano Semanal */}
          <Card>
            <CardHeader>
              <CardTitle>Plano Semanal</CardTitle>
              <CardDescription>Seus treinos programados para esta semana</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {workoutPlan?.workouts?.map((workout, index) => {
                  const workoutDate = new Date(workout.date);
                  const isToday = workoutDate.toDateString() === new Date().toDateString();
                  const isPast = workoutDate < new Date() && !isToday;
                  
                  return (
                    <div 
                      key={index}
                      className={`flex items-center justify-between p-4 rounded-lg border ${
                        isToday ? 'border-blue-200 bg-blue-50' : 
                        isPast ? 'border-gray-200 bg-gray-50' : 'border-gray-200'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          isToday ? 'bg-blue-600 text-white' : 
                          isPast ? 'bg-gray-400 text-white' : 'bg-gray-200 text-gray-600'
                        }`}>
                          {isPast ? <CheckCircle className="w-5 h-5" /> : <Dumbbell className="w-5 h-5" />}
                        </div>
                        <div>
                          <h3 className="font-medium">{workout.name}</h3>
                          <p className="text-sm text-gray-600">
                            {workoutDate.toLocaleDateString('pt-BR', { 
                              weekday: 'long', 
                              day: 'numeric', 
                              month: 'short' 
                            })}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">
                          {workout.exercises?.length || 0} exercícios
                        </Badge>
                        {!isPast && (
                          <Button 
                            size="sm" 
                            variant={isToday ? "default" : "outline"}
                            onClick={() => startWorkout(workout)}
                          >
                            <Play className="w-3 h-3 mr-1" />
                            Iniciar
                          </Button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Treino Ativo */}
        <TabsContent value="active" className="space-y-6">
          {currentWorkout ? (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{currentWorkout.name}</CardTitle>
                    <CardDescription>
                      Iniciado às {currentWorkout.startTime.toLocaleTimeString('pt-BR', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </CardDescription>
                  </div>
                  <Button variant="destructive" onClick={finishWorkout}>
                    Finalizar Treino
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {currentWorkout.exercises.map((exercise, exerciseIndex) => (
                    <div key={exerciseIndex} className="border rounded-lg p-4">
                      <h3 className="font-semibold mb-3">{exercise.name}</h3>
                      <div className="space-y-2">
                        {exercise.sets.map((set, setIndex) => (
                          <div 
                            key={setIndex}
                            className={`flex items-center justify-between p-3 rounded border ${
                              set.completed ? 'bg-green-50 border-green-200' : 'bg-gray-50'
                            }`}
                          >
                            <span className="text-sm">
                              Série {setIndex + 1}: {set.reps} repetições
                              {set.weight && ` - ${set.weight}kg`}
                            </span>
                            <Button
                              size="sm"
                              variant={set.completed ? "default" : "outline"}
                              onClick={() => completeSet(exerciseIndex, setIndex)}
                              disabled={set.completed}
                            >
                              {set.completed ? (
                                <>
                                  <CheckCircle className="w-3 h-3 mr-1" />
                                  Concluída
                                </>
                              ) : (
                                'Marcar'
                              )}
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Dumbbell className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-600 mb-2">
                  Nenhum treino ativo
                </h3>
                <p className="text-gray-500 mb-4">
                  Inicie um treino na aba "Plano" para começar
                </p>
                <Button onClick={() => setActiveTab('plan')}>
                  Ver Planos de Treino
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Histórico */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5" />
                <span>Histórico de Treinos</span>
              </CardTitle>
              <CardDescription>Seus últimos treinos realizados</CardDescription>
            </CardHeader>
            <CardContent>
              {workoutHistory.length > 0 ? (
                <div className="space-y-3">
                  {workoutHistory.map((workout, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        </div>
                        <div>
                          <h3 className="font-medium">{workout.name}</h3>
                          <p className="text-sm text-gray-600">
                            {new Date(workout.date).toLocaleDateString('pt-BR')} • {workout.duration}min
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{workout.exercises_count} exercícios</p>
                        <p className="text-xs text-gray-500">{workout.total_sets} séries</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">
                    Nenhum treino realizado
                  </h3>
                  <p className="text-gray-500">
                    Complete seu primeiro treino para ver o histórico aqui
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

export default Workouts;


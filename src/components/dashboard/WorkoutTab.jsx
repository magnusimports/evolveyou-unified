import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Dumbbell, 
  Target, 
  Clock, 
  Play,
  CheckCircle,
  Calendar,
  TrendingUp,
  Zap,
  Heart,
  Timer,
  RotateCcw
} from 'lucide-react';

const WorkoutTab = ({ userProfile }) => {
  const [selectedDay, setSelectedDay] = useState('monday');
  const [activeWorkout, setActiveWorkout] = useState(null);
  
  const anamneseAnswers = userProfile.anamneseAnswers || {};
  const primaryGoal = anamneseAnswers.primary_goal;
  const activityLevel = anamneseAnswers.activity_level;

  // Plano de treino baseado no perfil do usuário
  const workoutPlan = {
    monday: {
      name: 'Peito e Tríceps',
      duration: 60,
      difficulty: primaryGoal === 'muscle_gain' ? 'Avançado' : 'Intermediário',
      exercises: [
        { name: 'Supino reto com barra', sets: 4, reps: '8-10', rest: 90, completed: true },
        { name: 'Supino inclinado com halteres', sets: 3, reps: '10-12', rest: 60, completed: true },
        { name: 'Crucifixo inclinado', sets: 3, reps: '12-15', rest: 60, completed: false },
        { name: 'Paralelas', sets: 3, reps: '8-12', rest: 90, completed: false },
        { name: 'Tríceps testa', sets: 3, reps: '10-12', rest: 60, completed: false },
        { name: 'Tríceps corda', sets: 3, reps: '12-15', rest: 45, completed: false }
      ]
    },
    tuesday: {
      name: 'Costas e Bíceps',
      duration: 65,
      difficulty: 'Intermediário',
      exercises: [
        { name: 'Puxada frontal', sets: 4, reps: '8-10', rest: 90, completed: false },
        { name: 'Remada curvada', sets: 4, reps: '8-10', rest: 90, completed: false },
        { name: 'Remada sentado', sets: 3, reps: '10-12', rest: 60, completed: false },
        { name: 'Pullover', sets: 3, reps: '12-15', rest: 60, completed: false },
        { name: 'Rosca direta', sets: 3, reps: '10-12', rest: 60, completed: false },
        { name: 'Rosca martelo', sets: 3, reps: '12-15', rest: 45, completed: false }
      ]
    },
    wednesday: {
      name: 'Cardio e Core',
      duration: 45,
      difficulty: 'Moderado',
      exercises: [
        { name: 'Esteira - aquecimento', sets: 1, reps: '10 min', rest: 0, completed: false },
        { name: 'Bike - intervalado', sets: 5, reps: '2 min', rest: 60, completed: false },
        { name: 'Prancha', sets: 3, reps: '45-60s', rest: 30, completed: false },
        { name: 'Abdominal bicicleta', sets: 3, reps: '20 cada', rest: 30, completed: false },
        { name: 'Russian twist', sets: 3, reps: '30', rest: 30, completed: false },
        { name: 'Mountain climbers', sets: 3, reps: '30s', rest: 30, completed: false }
      ]
    },
    thursday: {
      name: 'Pernas',
      duration: 70,
      difficulty: 'Avançado',
      exercises: [
        { name: 'Agachamento livre', sets: 4, reps: '8-10', rest: 120, completed: false },
        { name: 'Leg press 45°', sets: 4, reps: '12-15', rest: 90, completed: false },
        { name: 'Stiff', sets: 3, reps: '10-12', rest: 90, completed: false },
        { name: 'Cadeira extensora', sets: 3, reps: '12-15', rest: 60, completed: false },
        { name: 'Mesa flexora', sets: 3, reps: '12-15', rest: 60, completed: false },
        { name: 'Panturrilha em pé', sets: 4, reps: '15-20', rest: 45, completed: false }
      ]
    },
    friday: {
      name: 'Ombros e Abdômen',
      duration: 55,
      difficulty: 'Intermediário',
      exercises: [
        { name: 'Desenvolvimento militar', sets: 4, reps: '8-10', rest: 90, completed: false },
        { name: 'Elevação lateral', sets: 3, reps: '12-15', rest: 60, completed: false },
        { name: 'Elevação posterior', sets: 3, reps: '12-15', rest: 60, completed: false },
        { name: 'Encolhimento', sets: 3, reps: '12-15', rest: 60, completed: false },
        { name: 'Abdominal supra', sets: 4, reps: '15-20', rest: 30, completed: false },
        { name: 'Elevação de pernas', sets: 3, reps: '12-15', rest: 30, completed: false }
      ]
    }
  };

  const weeklyStats = {
    workoutsCompleted: 3,
    totalWorkouts: 5,
    totalTime: 185, // minutos
    avgIntensity: 8.2,
    streak: 5
  };

  const currentWorkout = workoutPlan[selectedDay];
  const completedExercises = currentWorkout.exercises.filter(ex => ex.completed).length;
  const workoutProgress = (completedExercises / currentWorkout.exercises.length) * 100;

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Iniciante': return 'bg-green-100 text-green-800';
      case 'Moderado': return 'bg-yellow-100 text-yellow-800';
      case 'Intermediário': return 'bg-blue-100 text-blue-800';
      case 'Avançado': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRecommendations = () => {
    if (primaryGoal === 'weight_loss') {
      return [
        'Foque em exercícios compostos para queimar mais calorias',
        'Adicione mais cardio entre os treinos de força',
        'Mantenha intervalos de descanso menores (45-60s)',
        'Considere treinos em circuito para maior gasto calórico'
      ];
    } else if (primaryGoal === 'muscle_gain') {
      return [
        'Priorize exercícios compostos com cargas progressivas',
        'Descanso adequado entre séries (60-120s)',
        'Foque na execução perfeita dos movimentos',
        'Aumente gradualmente a carga a cada semana'
      ];
    } else if (primaryGoal === 'performance') {
      return [
        'Varie intensidades e volumes de treino',
        'Inclua exercícios pliométricos e funcionais',
        'Trabalhe mobilidade e flexibilidade',
        'Monitore recuperação entre sessões'
      ];
    }
    return [
      'Mantenha consistência nos treinos',
      'Combine força e cardio moderadamente',
      'Escute seu corpo e ajuste intensidade',
      'Foque em movimentos que você gosta'
    ];
  };

  return (
    <div className="space-y-6">
      {/* Estatísticas Semanais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Treinos</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{weeklyStats.workoutsCompleted}/{weeklyStats.totalWorkouts}</div>
            <p className="text-xs text-muted-foreground">
              Esta semana
            </p>
            <Progress 
              value={(weeklyStats.workoutsCompleted / weeklyStats.totalWorkouts) * 100} 
              className="mt-2" 
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tempo Total</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.floor(weeklyStats.totalTime / 60)}h {weeklyStats.totalTime % 60}m</div>
            <p className="text-xs text-muted-foreground">
              Tempo ativo
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Intensidade</CardTitle>
            <Zap className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{weeklyStats.avgIntensity}/10</div>
            <p className="text-xs text-muted-foreground">
              Média semanal
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sequência</CardTitle>
            <Target className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{weeklyStats.streak}</div>
            <p className="text-xs text-muted-foreground">
              Dias consecutivos
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Plano de Treino Semanal */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Plano Semanal
            </CardTitle>
            <CardDescription>
              Treino personalizado para {
                primaryGoal === 'weight_loss' ? 'perda de peso' :
                primaryGoal === 'muscle_gain' ? 'ganho de massa' :
                primaryGoal === 'performance' ? 'performance' : 'condicionamento geral'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={selectedDay} onValueChange={setSelectedDay}>
              <TabsList className="grid w-full grid-cols-5 text-xs">
                <TabsTrigger value="monday">Seg</TabsTrigger>
                <TabsTrigger value="tuesday">Ter</TabsTrigger>
                <TabsTrigger value="wednesday">Qua</TabsTrigger>
                <TabsTrigger value="thursday">Qui</TabsTrigger>
                <TabsTrigger value="friday">Sex</TabsTrigger>
              </TabsList>

              {Object.entries(workoutPlan).map(([day, workout]) => (
                <TabsContent key={day} value={day} className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">{workout.name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="text-xs">
                          <Clock className="h-3 w-3 mr-1" />
                          {workout.duration}min
                        </Badge>
                        <Badge className={`text-xs ${getDifficultyColor(workout.difficulty)}`}>
                          {workout.difficulty}
                        </Badge>
                      </div>
                    </div>
                    <Button 
                      size="sm"
                      onClick={() => setActiveWorkout(activeWorkout === day ? null : day)}
                      variant={activeWorkout === day ? "default" : "outline"}
                    >
                      {activeWorkout === day ? (
                        <>
                          <Timer className="h-4 w-4 mr-2" />
                          Pausar
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-2" />
                          Iniciar
                        </>
                      )}
                    </Button>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Progresso</span>
                      <span>{completedExercises}/{workout.exercises.length} exercícios</span>
                    </div>
                    <Progress value={workoutProgress} />
                  </div>

                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {workout.exercises.map((exercise, index) => (
                      <div 
                        key={index} 
                        className={`flex items-center justify-between p-3 rounded-lg border ${
                          exercise.completed ? 'bg-green-50 border-green-200' : 'bg-muted'
                        }`}
                      >
                        <div className="flex-1">
                          <p className={`text-sm font-medium ${
                            exercise.completed ? 'text-green-800 line-through' : ''
                          }`}>
                            {exercise.name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {exercise.sets} séries × {exercise.reps} reps
                            {exercise.rest > 0 && ` • ${exercise.rest}s descanso`}
                          </p>
                        </div>
                        {exercise.completed && (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        )}
                      </div>
                    ))}
                  </div>
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>

        {/* Histórico e Progresso */}
        <div className="space-y-6">
          {/* Progresso do Treino Atual */}
          {activeWorkout && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Timer className="h-5 w-5 text-blue-600" />
                  Treino em Andamento
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold">
                      {workoutPlan[activeWorkout].name}
                    </span>
                    <Badge variant="outline" className="animate-pulse">
                      Ativo
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Tempo decorrido:</span>
                      <p className="font-medium">23:45</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Exercício atual:</span>
                      <p className="font-medium">3/6</p>
                    </div>
                  </div>

                  <Progress value={50} className="h-2" />
                  
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Reiniciar
                    </Button>
                    <Button size="sm" className="flex-1">
                      Próximo Exercício
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Histórico da Semana */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Histórico da Semana
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { day: 'Segunda', workout: 'Peito e Tríceps', duration: 62, completed: true },
                  { day: 'Terça', workout: 'Costas e Bíceps', duration: 58, completed: true },
                  { day: 'Quarta', workout: 'Cardio e Core', duration: 45, completed: true },
                  { day: 'Quinta', workout: 'Pernas', duration: 0, completed: false },
                  { day: 'Sexta', workout: 'Ombros e Abdômen', duration: 0, completed: false }
                ].map((session, index) => (
                  <div key={index} className="flex items-center justify-between p-2 rounded">
                    <div className="flex items-center gap-3">
                      {session.completed ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : (
                        <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
                      )}
                      <div>
                        <p className="text-sm font-medium">{session.day}</p>
                        <p className="text-xs text-muted-foreground">{session.workout}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      {session.completed ? (
                        <p className="text-sm font-medium">{session.duration}min</p>
                      ) : (
                        <p className="text-xs text-muted-foreground">Pendente</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Dicas Personalizadas */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="h-5 w-5" />
                Dicas Personalizadas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {getRecommendations().map((tip, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                    <p className="text-sm">{tip}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default WorkoutTab;


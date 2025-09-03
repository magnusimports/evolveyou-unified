import React, { useState, useEffect, useRef } from 'react';
import { exerciseCategories } from '../../data/exerciseDatabase';

const WorkoutPlayer = ({ workout, onFinishWorkout, onExitWorkout }) => {
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [currentSet, setCurrentSet] = useState(1);
  const [isResting, setIsResting] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [completedSets, setCompletedSets] = useState({});
  const [workoutStartTime, setWorkoutStartTime] = useState(null);
  const [exerciseStartTime, setExerciseStartTime] = useState(null);
  const [showExerciseDetails, setShowExerciseDetails] = useState(false);
  const [actualWeight, setActualWeight] = useState(0);
  const [actualReps, setActualReps] = useState('');
  const [exerciseNotes, setExerciseNotes] = useState('');

  const timerRef = useRef(null);
  const audioRef = useRef(null);

  const currentExercise = workout.exercises[currentExerciseIndex];
  const totalExercises = workout.exercises.length;
  const progress = ((currentExerciseIndex + (currentSet - 1) / currentExercise?.sets) / totalExercises) * 100;

  // Inicializar workout
  useEffect(() => {
    if (!workoutStartTime) {
      setWorkoutStartTime(new Date());
      setExerciseStartTime(new Date());
      setActualWeight(currentExercise?.weight || 0);
      setActualReps(currentExercise?.reps || '');
    }
  }, []);

  // Timer
  useEffect(() => {
    if (isPlaying && timeRemaining > 0) {
      timerRef.current = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            playNotificationSound();
            if (isResting) {
              setIsResting(false);
              setIsPlaying(false);
            }
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }

    return () => clearInterval(timerRef.current);
  }, [isPlaying, timeRemaining, isResting]);

  const playNotificationSound = () => {
    // Som de notificação (você pode adicionar um arquivo de áudio)
    if (audioRef.current) {
      audioRef.current.play().catch(() => {
        // Fallback para navegadores que não permitem autoplay
        console.log('Audio notification blocked');
      });
    }
  };

  const startRestTimer = () => {
    setIsResting(true);
    setTimeRemaining(currentExercise.restTime);
    setIsPlaying(true);
  };

  const skipRest = () => {
    setIsResting(false);
    setIsPlaying(false);
    setTimeRemaining(0);
  };

  const completeSet = () => {
    const setKey = `${currentExercise.id}_${currentSet}`;
    setCompletedSets(prev => ({
      ...prev,
      [setKey]: {
        weight: actualWeight,
        reps: actualReps,
        notes: exerciseNotes,
        completedAt: new Date()
      }
    }));

    if (currentSet < currentExercise.sets) {
      // Próxima série
      setCurrentSet(prev => prev + 1);
      startRestTimer();
    } else {
      // Próximo exercício
      nextExercise();
    }
  };

  const nextExercise = () => {
    if (currentExerciseIndex < totalExercises - 1) {
      setCurrentExerciseIndex(prev => prev + 1);
      setCurrentSet(1);
      setExerciseStartTime(new Date());
      setIsResting(false);
      setIsPlaying(false);
      setTimeRemaining(0);
      
      // Reset valores para próximo exercício
      const nextEx = workout.exercises[currentExerciseIndex + 1];
      setActualWeight(nextEx?.weight || 0);
      setActualReps(nextEx?.reps || '');
      setExerciseNotes('');
    } else {
      // Treino finalizado
      finishWorkout();
    }
  };

  const previousExercise = () => {
    if (currentExerciseIndex > 0) {
      setCurrentExerciseIndex(prev => prev - 1);
      setCurrentSet(1);
      setIsResting(false);
      setIsPlaying(false);
      setTimeRemaining(0);
      
      // Reset valores para exercício anterior
      const prevEx = workout.exercises[currentExerciseIndex - 1];
      setActualWeight(prevEx?.weight || 0);
      setActualReps(prevEx?.reps || '');
      setExerciseNotes('');
    }
  };

  const finishWorkout = () => {
    const workoutData = {
      workoutId: workout.id,
      workoutName: workout.name,
      startTime: workoutStartTime,
      endTime: new Date(),
      duration: Math.round((new Date() - workoutStartTime) / 1000 / 60), // em minutos
      completedSets,
      exercises: workout.exercises.map(ex => ({
        ...ex,
        completed: true
      }))
    };
    
    onFinishWorkout && onFinishWorkout(workoutData);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getElapsedTime = () => {
    if (!workoutStartTime) return '0:00';
    const elapsed = Math.floor((new Date() - workoutStartTime) / 1000);
    return formatTime(elapsed);
  };

  const categoryInfo = exerciseCategories.find(cat => cat.id === currentExercise?.categoria);

  if (!currentExercise) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-center">
        <div className="text-4xl mb-4">⚠️</div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Treino não encontrado</h2>
        <button
          onClick={onExitWorkout}
          className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium"
        >
          Voltar
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Audio para notificações */}
      <audio ref={audioRef} preload="auto">
        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT" type="audio/wav" />
      </audio>

      {/* Header do Treino */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-2xl font-bold">{workout.name}</h1>
            <p className="opacity-90">{workout.description}</p>
          </div>
          <button
            onClick={onExitWorkout}
            className="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            ❌ Sair
          </button>
        </div>

        {/* Progresso */}
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span>Progresso do Treino</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-white bg-opacity-20 rounded-full h-2">
            <div 
              className="bg-white h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Estatísticas */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-bold">{currentExerciseIndex + 1}/{totalExercises}</div>
            <div className="text-sm opacity-90">Exercício</div>
          </div>
          <div>
            <div className="text-lg font-bold">{currentSet}/{currentExercise.sets}</div>
            <div className="text-sm opacity-90">Série</div>
          </div>
          <div>
            <div className="text-lg font-bold">{getElapsedTime()}</div>
            <div className="text-sm opacity-90">Tempo</div>
          </div>
        </div>
      </div>

      {/* Timer de Descanso */}
      {isResting && (
        <div className="bg-orange-500 rounded-xl p-6 text-white text-center mb-6">
          <h2 className="text-2xl font-bold mb-2">⏱️ Descanso</h2>
          <div className="text-4xl font-bold mb-4">{formatTime(timeRemaining)}</div>
          <div className="flex justify-center gap-4">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="bg-white bg-opacity-20 hover:bg-opacity-30 px-6 py-2 rounded-lg font-medium"
            >
              {isPlaying ? '⏸️ Pausar' : '▶️ Continuar'}
            </button>
            <button
              onClick={skipRest}
              className="bg-white bg-opacity-20 hover:bg-opacity-30 px-6 py-2 rounded-lg font-medium"
            >
              ⏭️ Pular
            </button>
          </div>
        </div>
      )}

      {/* Exercício Atual */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="flex justify-between items-start mb-6">
          <div className="flex items-center gap-4">
            <div className={`w-4 h-4 rounded-full ${categoryInfo?.color}`}></div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{currentExercise.nome}</h2>
              <p className="text-gray-600 capitalize">
                {categoryInfo?.icon} {categoryInfo?.nome} • {currentExercise.tipo_movimento}
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowExerciseDetails(!showExerciseDetails)}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium"
          >
            {showExerciseDetails ? '👁️ Ocultar' : '👁️ Detalhes'}
          </button>
        </div>

        {/* Detalhes do Exercício */}
        {showExerciseDetails && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">📋 Como Executar:</h4>
                <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
                  {currentExercise.instrucoes.map((instrucao, index) => (
                    <li key={index}>{instrucao}</li>
                  ))}
                </ol>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">💡 Dicas:</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                  {currentExercise.dicas.map((dica, index) => (
                    <li key={index}>{dica}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Configuração da Série */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Peso (kg)</label>
            <input
              type="number"
              min="0"
              step="0.5"
              value={actualWeight}
              onChange={(e) => setActualWeight(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Repetições</label>
            <input
              type="text"
              value={actualReps}
              onChange={(e) => setActualReps(e.target.value)}
              placeholder={currentExercise.reps}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Meta</label>
            <div className="px-3 py-2 bg-gray-100 rounded-lg text-gray-700">
              {currentExercise.weight}kg × {currentExercise.reps}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Descanso</label>
            <div className="px-3 py-2 bg-gray-100 rounded-lg text-gray-700">
              {formatTime(currentExercise.restTime)}
            </div>
          </div>
        </div>

        {/* Notas da Série */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">Notas desta série (opcional)</label>
          <input
            type="text"
            value={exerciseNotes}
            onChange={(e) => setExerciseNotes(e.target.value)}
            placeholder="Como foi a execução? Dificuldades? Sensações..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Histórico de Séries Completadas */}
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-2">📊 Séries Completadas:</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
            {Array.from({ length: currentExercise.sets }, (_, index) => {
              const setNumber = index + 1;
              const setKey = `${currentExercise.id}_${setNumber}`;
              const setData = completedSets[setKey];
              const isCurrentSet = setNumber === currentSet;
              const isCompleted = !!setData;

              return (
                <div
                  key={setNumber}
                  className={`p-3 rounded-lg border ${
                    isCurrentSet
                      ? 'border-blue-500 bg-blue-50'
                      : isCompleted
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium">
                      Série {setNumber}
                      {isCurrentSet && ' (atual)'}
                      {isCompleted && ' ✅'}
                    </span>
                  </div>
                  {isCompleted && (
                    <div className="text-sm text-gray-600 mt-1">
                      {setData.weight}kg × {setData.reps}
                      {setData.notes && (
                        <div className="text-xs italic mt-1">{setData.notes}</div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Botões de Controle */}
        <div className="flex flex-wrap gap-4 justify-center">
          <button
            onClick={previousExercise}
            disabled={currentExerciseIndex === 0}
            className="px-6 py-3 bg-gray-500 hover:bg-gray-600 disabled:bg-gray-300 text-white rounded-lg font-medium"
          >
            ⬅️ Anterior
          </button>
          
          {!isResting && (
            <button
              onClick={completeSet}
              className="px-8 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium text-lg"
            >
              ✅ Série Completa
            </button>
          )}
          
          <button
            onClick={nextExercise}
            disabled={currentExerciseIndex === totalExercises - 1 && currentSet === currentExercise.sets}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white rounded-lg font-medium"
          >
            {currentExerciseIndex === totalExercises - 1 ? '🏁 Finalizar' : '➡️ Próximo'}
          </button>
        </div>
      </div>

      {/* Próximo Exercício Preview */}
      {currentExerciseIndex < totalExercises - 1 && (
        <div className="bg-gray-50 rounded-xl p-4">
          <h3 className="font-medium text-gray-900 mb-2">🔮 Próximo Exercício:</h3>
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-gray-400"></div>
            <span className="text-gray-700">{workout.exercises[currentExerciseIndex + 1].nome}</span>
            <span className="text-sm text-gray-500">
              {workout.exercises[currentExerciseIndex + 1].sets} séries × {workout.exercises[currentExerciseIndex + 1].reps}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkoutPlayer;


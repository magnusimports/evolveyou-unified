import React, { useState, useRef } from 'react';
import ExerciseLibrary from './ExerciseLibrary';
import { exerciseCategories, difficultyLevels } from '../../data/exerciseDatabase';

const WorkoutBuilder = ({ onSaveWorkout, userProfile }) => {
  const [workoutName, setWorkoutName] = useState('');
  const [workoutDescription, setWorkoutDescription] = useState('');
  const [selectedExercises, setSelectedExercises] = useState([]);
  const [currentTab, setCurrentTab] = useState('library'); // library, builder, templates
  const [draggedExercise, setDraggedExercise] = useState(null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const dragCounter = useRef(0);

  // Templates de treino pré-definidos
  const workoutTemplates = [
    {
      id: 'push',
      name: 'Push (Empurrar)',
      description: 'Peito, Ombros e Tríceps',
      exercises: ['chest_001', 'chest_002', 'shoulders_001', 'shoulders_002', 'triceps_001', 'triceps_002'],
      duration: '60-75 min',
      difficulty: 'intermediario'
    },
    {
      id: 'pull',
      name: 'Pull (Puxar)',
      description: 'Costas e Bíceps',
      exercises: ['back_001', 'back_002', 'back_003', 'back_004', 'biceps_001', 'biceps_002'],
      duration: '60-75 min',
      difficulty: 'intermediario'
    },
    {
      id: 'legs',
      name: 'Legs (Pernas)',
      description: 'Quadríceps, Posteriores e Glúteos',
      exercises: ['quads_001', 'quads_002', 'hamstrings_001', 'glutes_001', 'calves_001'],
      duration: '75-90 min',
      difficulty: 'intermediario'
    },
    {
      id: 'upper',
      name: 'Upper Body',
      description: 'Parte Superior Completa',
      exercises: ['chest_001', 'back_001', 'shoulders_001', 'biceps_001', 'triceps_001'],
      duration: '90-105 min',
      difficulty: 'avancado'
    },
    {
      id: 'fullbody',
      name: 'Full Body',
      description: 'Corpo Inteiro',
      exercises: ['quads_001', 'chest_001', 'back_001', 'shoulders_001', 'abs_001'],
      duration: '60-75 min',
      difficulty: 'iniciante'
    }
  ];

  const handleSelectExercise = (exercise) => {
    const isAlreadySelected = selectedExercises.find(ex => ex.id === exercise.id);
    
    if (isAlreadySelected) {
      // Remove se já estiver selecionado
      setSelectedExercises(prev => prev.filter(ex => ex.id !== exercise.id));
    } else {
      // Adiciona com configurações padrão
      const exerciseWithConfig = {
        ...exercise,
        sets: parseInt(exercise.series_recomendadas.split('-')[0]) || 3,
        reps: exercise.repeticoes_recomendadas,
        weight: 0,
        restTime: exercise.descanso_segundos,
        notes: ''
      };
      setSelectedExercises(prev => [...prev, exerciseWithConfig]);
    }
  };

  const handleRemoveExercise = (exerciseId) => {
    setSelectedExercises(prev => prev.filter(ex => ex.id !== exerciseId));
  };

  const handleUpdateExercise = (exerciseId, updates) => {
    setSelectedExercises(prev => 
      prev.map(ex => ex.id === exerciseId ? { ...ex, ...updates } : ex)
    );
  };

  const handleDragStart = (e, exercise) => {
    setDraggedExercise(exercise);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    dragCounter.current++;
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    dragCounter.current--;
  };

  const handleDrop = (e, targetIndex) => {
    e.preventDefault();
    dragCounter.current = 0;
    
    if (!draggedExercise) return;

    const sourceIndex = selectedExercises.findIndex(ex => ex.id === draggedExercise.id);
    if (sourceIndex === -1 || sourceIndex === targetIndex) return;

    const newExercises = [...selectedExercises];
    const [removed] = newExercises.splice(sourceIndex, 1);
    newExercises.splice(targetIndex, 0, removed);
    
    setSelectedExercises(newExercises);
    setDraggedExercise(null);
  };

  const calculateWorkoutStats = () => {
    const totalExercises = selectedExercises.length;
    const totalSets = selectedExercises.reduce((sum, ex) => sum + ex.sets, 0);
    const estimatedDuration = selectedExercises.reduce((sum, ex) => {
      // Estima 2 min por série + tempo de descanso
      return sum + (ex.sets * 2) + (ex.sets * ex.restTime / 60);
    }, 0);
    const totalCalories = selectedExercises.reduce((sum, ex) => sum + (ex.sets * ex.calorias_por_serie), 0);

    return {
      totalExercises,
      totalSets,
      estimatedDuration: Math.round(estimatedDuration),
      totalCalories: Math.round(totalCalories)
    };
  };

  const handleSaveWorkout = () => {
    if (!workoutName.trim()) {
      alert('Por favor, digite um nome para o treino');
      return;
    }

    if (selectedExercises.length === 0) {
      alert('Adicione pelo menos um exercício ao treino');
      return;
    }

    const workout = {
      id: Date.now().toString(),
      name: workoutName,
      description: workoutDescription,
      exercises: selectedExercises,
      stats: calculateWorkoutStats(),
      createdAt: new Date(),
      userId: userProfile?.uid
    };

    onSaveWorkout && onSaveWorkout(workout);
    setShowSaveDialog(false);
    
    // Reset form
    setWorkoutName('');
    setWorkoutDescription('');
    setSelectedExercises([]);
  };

  const loadTemplate = (template) => {
    // Aqui você carregaria os exercícios do template
    // Por simplicidade, vou simular
    setWorkoutName(template.name);
    setWorkoutDescription(template.description);
    // setSelectedExercises(template.exercises.map(id => getExerciseById(id)));
    setCurrentTab('builder');
  };

  const stats = calculateWorkoutStats();

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Construtor de Treinos</h1>
        <p className="text-gray-600">Monte seu treino personalizado com nossa biblioteca de exercícios</p>
      </div>

      {/* Navegação */}
      <div className="flex justify-center mb-8">
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setCurrentTab('library')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              currentTab === 'library'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            📚 Biblioteca
          </button>
          <button
            onClick={() => setCurrentTab('builder')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              currentTab === 'builder'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            🏗️ Construtor ({selectedExercises.length})
          </button>
          <button
            onClick={() => setCurrentTab('templates')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              currentTab === 'templates'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            📋 Templates
          </button>
        </div>
      </div>

      {/* Conteúdo das Abas */}
      {currentTab === 'library' && (
        <ExerciseLibrary 
          onSelectExercise={handleSelectExercise}
          selectedExercises={selectedExercises}
        />
      )}

      {currentTab === 'builder' && (
        <WorkoutBuilderTab
          selectedExercises={selectedExercises}
          onRemoveExercise={handleRemoveExercise}
          onUpdateExercise={handleUpdateExercise}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          stats={stats}
          onSave={() => setShowSaveDialog(true)}
        />
      )}

      {currentTab === 'templates' && (
        <WorkoutTemplatesTab
          templates={workoutTemplates}
          onLoadTemplate={loadTemplate}
        />
      )}

      {/* Dialog de Salvar Treino */}
      {showSaveDialog && (
        <SaveWorkoutDialog
          workoutName={workoutName}
          setWorkoutName={setWorkoutName}
          workoutDescription={workoutDescription}
          setWorkoutDescription={setWorkoutDescription}
          stats={stats}
          onSave={handleSaveWorkout}
          onCancel={() => setShowSaveDialog(false)}
        />
      )}
    </div>
  );
};

// Aba do Construtor
const WorkoutBuilderTab = ({ 
  selectedExercises, 
  onRemoveExercise, 
  onUpdateExercise,
  onDragStart,
  onDragOver,
  onDragEnter,
  onDragLeave,
  onDrop,
  stats,
  onSave
}) => {
  if (selectedExercises.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🏗️</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Seu treino está vazio</h3>
        <p className="text-gray-600 mb-6">
          Vá para a Biblioteca e adicione exercícios para começar a montar seu treino
        </p>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
          <h4 className="font-medium text-blue-900 mb-2">💡 Dica:</h4>
          <p className="text-blue-800 text-sm">
            Você pode usar os Templates prontos ou criar seu treino do zero na Biblioteca
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Estatísticas do Treino */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white">
        <h2 className="text-xl font-semibold mb-4">📊 Estatísticas do Treino</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{stats.totalExercises}</div>
            <div className="text-sm opacity-90">Exercícios</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{stats.totalSets}</div>
            <div className="text-sm opacity-90">Séries Total</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{stats.estimatedDuration}min</div>
            <div className="text-sm opacity-90">Duração Estimada</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{stats.totalCalories}</div>
            <div className="text-sm opacity-90">Calorias Estimadas</div>
          </div>
        </div>
      </div>

      {/* Lista de Exercícios */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Exercícios do Treino</h3>
          <button
            onClick={onSave}
            className="px-6 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium"
          >
            💾 Salvar Treino
          </button>
        </div>

        <div className="space-y-4">
          {selectedExercises.map((exercise, index) => (
            <ExerciseBuilderCard
              key={exercise.id}
              exercise={exercise}
              index={index}
              onRemove={onRemoveExercise}
              onUpdate={onUpdateExercise}
              onDragStart={onDragStart}
              onDragOver={onDragOver}
              onDragEnter={onDragEnter}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
            />
          ))}
        </div>

        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800 text-sm">
            💡 <strong>Dica:</strong> Arraste os exercícios para reordená-los. 
            Ajuste séries, repetições e peso para personalizar seu treino.
          </p>
        </div>
      </div>
    </div>
  );
};

// Card de Exercício no Construtor
const ExerciseBuilderCard = ({ 
  exercise, 
  index, 
  onRemove, 
  onUpdate,
  onDragStart,
  onDragOver,
  onDragEnter,
  onDragLeave,
  onDrop
}) => {
  const categoryInfo = exerciseCategories.find(cat => cat.id === exercise.categoria);

  return (
    <div
      draggable
      onDragStart={(e) => onDragStart(e, exercise)}
      onDragOver={onDragOver}
      onDragEnter={onDragEnter}
      onDragLeave={onDragLeave}
      onDrop={(e) => onDrop(e, index)}
      className="bg-gray-50 border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all cursor-move"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="text-gray-400">⋮⋮</div>
          <div className={`w-3 h-3 rounded-full ${categoryInfo?.color}`}></div>
          <div>
            <h4 className="font-medium text-gray-900">{exercise.nome}</h4>
            <p className="text-sm text-gray-600 capitalize">
              {categoryInfo?.nome} • {exercise.tipo_movimento}
            </p>
          </div>
        </div>
        <button
          onClick={() => onRemove(exercise.id)}
          className="text-red-500 hover:text-red-700 text-xl"
        >
          🗑️
        </button>
      </div>

      {/* Configurações do Exercício */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Séries</label>
          <input
            type="number"
            min="1"
            max="10"
            value={exercise.sets}
            onChange={(e) => onUpdate(exercise.id, { sets: parseInt(e.target.value) || 1 })}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Repetições</label>
          <input
            type="text"
            value={exercise.reps}
            onChange={(e) => onUpdate(exercise.id, { reps: e.target.value })}
            placeholder="8-12"
            className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Peso (kg)</label>
          <input
            type="number"
            min="0"
            step="0.5"
            value={exercise.weight}
            onChange={(e) => onUpdate(exercise.id, { weight: parseFloat(e.target.value) || 0 })}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Descanso (s)</label>
          <input
            type="number"
            min="30"
            max="300"
            step="15"
            value={exercise.restTime}
            onChange={(e) => onUpdate(exercise.id, { restTime: parseInt(e.target.value) || 60 })}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Notas */}
      <div className="mt-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Notas (opcional)</label>
        <input
          type="text"
          value={exercise.notes}
          onChange={(e) => onUpdate(exercise.id, { notes: e.target.value })}
          placeholder="Ex: Foco na fase excêntrica, usar pegada mais larga..."
          className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
};

// Aba de Templates
const WorkoutTemplatesTab = ({ templates, onLoadTemplate }) => {
  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Templates de Treino</h2>
        <p className="text-gray-600">Comece com um template pronto e personalize conforme sua necessidade</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => {
          const difficultyInfo = difficultyLevels.find(diff => diff.id === template.difficulty);
          
          return (
            <div key={template.id} className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
                  <p className="text-gray-600 text-sm">{template.description}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs text-white ${difficultyInfo?.color}`}>
                  {difficultyInfo?.nome}
                </span>
              </div>

              <div className="space-y-2 mb-6">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Exercícios:</span>
                  <span className="font-medium">{template.exercises.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Duração:</span>
                  <span className="font-medium">{template.duration}</span>
                </div>
              </div>

              <button
                onClick={() => onLoadTemplate(template)}
                className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
              >
                🚀 Usar Template
              </button>
            </div>
          );
        })}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-medium text-blue-900 mb-2">💡 Como usar os Templates:</h3>
        <ul className="text-blue-800 text-sm space-y-1">
          <li>• Escolha um template que combine com seu objetivo</li>
          <li>• Personalize os exercícios, séries e repetições</li>
          <li>• Ajuste os pesos conforme sua capacidade atual</li>
          <li>• Salve como seu treino personalizado</li>
        </ul>
      </div>
    </div>
  );
};

// Dialog para Salvar Treino
const SaveWorkoutDialog = ({ 
  workoutName, 
  setWorkoutName, 
  workoutDescription, 
  setWorkoutDescription, 
  stats, 
  onSave, 
  onCancel 
}) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h3 className="text-lg font-semibold mb-4">💾 Salvar Treino</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Treino</label>
            <input
              type="text"
              value={workoutName}
              onChange={(e) => setWorkoutName(e.target.value)}
              placeholder="Ex: Push Day, Treino de Peito..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Descrição (opcional)</label>
            <textarea
              value={workoutDescription}
              onChange={(e) => setWorkoutDescription(e.target.value)}
              placeholder="Descreva o foco do treino..."
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Resumo do Treino */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Resumo:</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>Exercícios: <span className="font-medium">{stats.totalExercises}</span></div>
              <div>Séries: <span className="font-medium">{stats.totalSets}</span></div>
              <div>Duração: <span className="font-medium">{stats.estimatedDuration}min</span></div>
              <div>Calorias: <span className="font-medium">{stats.totalCalories}</span></div>
            </div>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onSave}
            disabled={!workoutName.trim()}
            className="flex-1 bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white py-2 rounded-lg font-medium"
          >
            Salvar
          </button>
          <button
            onClick={onCancel}
            className="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-2 rounded-lg font-medium"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export default WorkoutBuilder;


import React, { useState, useMemo } from 'react';
import { 
  searchExercises, 
  getExercisesByCategory, 
  getExercisesByEquipment, 
  getExercisesByDifficulty,
  exerciseCategories,
  equipmentTypes,
  difficultyLevels
} from '../../data/exerciseDatabase';

const ExerciseLibrary = ({ onSelectExercise, selectedExercises = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedEquipment, setSelectedEquipment] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // grid ou list

  // Filtros combinados
  const filteredExercises = useMemo(() => {
    let exercises = searchExercises(searchTerm);
    
    if (selectedCategory) {
      exercises = exercises.filter(ex => ex.categoria === selectedCategory);
    }
    
    if (selectedEquipment) {
      exercises = exercises.filter(ex => ex.equipamento === selectedEquipment);
    }
    
    if (selectedDifficulty) {
      exercises = exercises.filter(ex => ex.dificuldade === selectedDifficulty);
    }
    
    return exercises;
  }, [searchTerm, selectedCategory, selectedEquipment, selectedDifficulty]);

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedCategory('');
    setSelectedEquipment('');
    setSelectedDifficulty('');
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Biblioteca de Exercícios</h1>
        <p className="text-gray-600">Mais de 40 exercícios detalhados para seu treino perfeito</p>
      </div>

      {/* Barra de Busca */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Buscar exercícios... (ex: supino, agachamento, bíceps)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <div className="absolute left-4 top-3.5 text-gray-400">
            🔍
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="mb-6 space-y-4">
        {/* Filtros Rápidos - Categorias */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Grupos Musculares</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('')}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                !selectedCategory 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              }`}
            >
              Todos
            </button>
            {exerciseCategories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  selectedCategory === category.id
                    ? `${category.color} text-white`
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
              >
                {category.icon} {category.nome}
              </button>
            ))}
          </div>
        </div>

        {/* Filtros Avançados */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Equipamento */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Equipamento</label>
            <select
              value={selectedEquipment}
              onChange={(e) => setSelectedEquipment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos os equipamentos</option>
              {equipmentTypes.map((equipment) => (
                <option key={equipment.id} value={equipment.id}>
                  {equipment.icon} {equipment.nome}
                </option>
              ))}
            </select>
          </div>

          {/* Dificuldade */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Dificuldade</label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todas as dificuldades</option>
              {difficultyLevels.map((level) => (
                <option key={level.id} value={level.id}>
                  {level.nome}
                </option>
              ))}
            </select>
          </div>

          {/* Modo de Visualização */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Visualização</label>
            <div className="flex rounded-lg border border-gray-300 overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={`flex-1 px-3 py-2 text-sm font-medium ${
                  viewMode === 'grid'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white hover:bg-gray-50 text-gray-700'
                }`}
              >
                📱 Cards
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`flex-1 px-3 py-2 text-sm font-medium ${
                  viewMode === 'list'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white hover:bg-gray-50 text-gray-700'
                }`}
              >
                📋 Lista
              </button>
            </div>
          </div>
        </div>

        {/* Botão Limpar Filtros */}
        {(searchTerm || selectedCategory || selectedEquipment || selectedDifficulty) && (
          <div className="flex justify-center">
            <button
              onClick={clearFilters}
              className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium"
            >
              🗑️ Limpar Filtros
            </button>
          </div>
        )}
      </div>

      {/* Resultados */}
      <div className="mb-4">
        <p className="text-gray-600">
          {filteredExercises.length} exercício{filteredExercises.length !== 1 ? 's' : ''} encontrado{filteredExercises.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Lista de Exercícios */}
      {viewMode === 'grid' ? (
        <ExerciseGrid 
          exercises={filteredExercises} 
          onSelectExercise={onSelectExercise}
          selectedExercises={selectedExercises}
        />
      ) : (
        <ExerciseList 
          exercises={filteredExercises} 
          onSelectExercise={onSelectExercise}
          selectedExercises={selectedExercises}
        />
      )}

      {/* Mensagem quando não há resultados */}
      {filteredExercises.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Nenhum exercício encontrado</h3>
          <p className="text-gray-600 mb-4">
            Tente ajustar os filtros ou usar termos de busca diferentes
          </p>
          <button
            onClick={clearFilters}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium"
          >
            Limpar Filtros
          </button>
        </div>
      )}
    </div>
  );
};

// Componente Grid de Exercícios
const ExerciseGrid = ({ exercises, onSelectExercise, selectedExercises }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {exercises.map((exercise) => (
        <ExerciseCard
          key={exercise.id}
          exercise={exercise}
          onSelect={onSelectExercise}
          isSelected={selectedExercises.some(ex => ex.id === exercise.id)}
        />
      ))}
    </div>
  );
};

// Componente Lista de Exercícios
const ExerciseList = ({ exercises, onSelectExercise, selectedExercises }) => {
  return (
    <div className="space-y-4">
      {exercises.map((exercise) => (
        <ExerciseListItem
          key={exercise.id}
          exercise={exercise}
          onSelect={onSelectExercise}
          isSelected={selectedExercises.some(ex => ex.id === exercise.id)}
        />
      ))}
    </div>
  );
};

// Card de Exercício
const ExerciseCard = ({ exercise, onSelect, isSelected }) => {
  const [showDetails, setShowDetails] = useState(false);
  
  const categoryInfo = exerciseCategories.find(cat => cat.id === exercise.categoria);
  const difficultyInfo = difficultyLevels.find(diff => diff.id === exercise.dificuldade);
  const equipmentInfo = equipmentTypes.find(eq => eq.id === exercise.equipamento);

  return (
    <div className={`bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden ${
      isSelected ? 'ring-2 ring-blue-500' : ''
    }`}>
      {/* Header do Card */}
      <div className={`${categoryInfo?.color || 'bg-gray-500'} p-4 text-white`}>
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-semibold text-lg">{exercise.nome}</h3>
            <p className="text-sm opacity-90 capitalize">
              {categoryInfo?.icon} {categoryInfo?.nome}
            </p>
          </div>
          <div className="text-2xl">{categoryInfo?.icon}</div>
        </div>
      </div>

      {/* Conteúdo do Card */}
      <div className="p-4">
        {/* Informações Básicas */}
        <div className="grid grid-cols-2 gap-2 mb-4 text-sm">
          <div className="flex items-center">
            <span className="text-gray-500">🏋️</span>
            <span className="ml-1">{equipmentInfo?.nome}</span>
          </div>
          <div className="flex items-center">
            <span className={`w-3 h-3 rounded-full ${difficultyInfo?.color} mr-2`}></span>
            <span>{difficultyInfo?.nome}</span>
          </div>
          <div className="flex items-center">
            <span className="text-gray-500">🔥</span>
            <span className="ml-1">{exercise.calorias_por_serie} kcal/série</span>
          </div>
          <div className="flex items-center">
            <span className="text-gray-500">⏱️</span>
            <span className="ml-1">{exercise.descanso_segundos}s descanso</span>
          </div>
        </div>

        {/* Músculos Trabalhados */}
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-1">Músculos Principais:</p>
          <div className="flex flex-wrap gap-1">
            {exercise.musculos_primarios.map((muscle, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
              >
                {muscle.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>

        {/* Séries e Repetições Recomendadas */}
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="font-medium text-gray-700">Séries:</span>
              <span className="ml-1">{exercise.series_recomendadas}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Reps:</span>
              <span className="ml-1">{exercise.repeticoes_recomendadas}</span>
            </div>
          </div>
        </div>

        {/* Botões de Ação */}
        <div className="flex gap-2">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="flex-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors"
          >
            {showDetails ? '👁️ Ocultar' : '👁️ Detalhes'}
          </button>
          <button
            onClick={() => onSelect && onSelect(exercise)}
            className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              isSelected
                ? 'bg-green-500 hover:bg-green-600 text-white'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {isSelected ? '✅ Selecionado' : '➕ Adicionar'}
          </button>
        </div>

        {/* Detalhes Expandidos */}
        {showDetails && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <ExerciseDetails exercise={exercise} />
          </div>
        )}
      </div>
    </div>
  );
};

// Item de Lista de Exercício
const ExerciseListItem = ({ exercise, onSelect, isSelected }) => {
  const [showDetails, setShowDetails] = useState(false);
  
  const categoryInfo = exerciseCategories.find(cat => cat.id === exercise.categoria);
  const difficultyInfo = difficultyLevels.find(diff => diff.id === exercise.dificuldade);
  const equipmentInfo = equipmentTypes.find(eq => eq.id === exercise.equipamento);

  return (
    <div className={`bg-white rounded-lg shadow hover:shadow-md transition-all p-4 ${
      isSelected ? 'ring-2 ring-blue-500' : ''
    }`}>
      <div className="flex items-center justify-between">
        {/* Informações Principais */}
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className={`w-3 h-3 rounded-full ${categoryInfo?.color}`}></div>
            <h3 className="font-semibold text-lg">{exercise.nome}</h3>
            <span className={`px-2 py-1 rounded-full text-xs ${difficultyInfo?.color} text-white`}>
              {difficultyInfo?.nome}
            </span>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>{categoryInfo?.icon} {categoryInfo?.nome}</span>
            <span>🏋️ {equipmentInfo?.nome}</span>
            <span>📊 {exercise.series_recomendadas} x {exercise.repeticoes_recomendadas}</span>
            <span>🔥 {exercise.calorias_por_serie} kcal</span>
          </div>
        </div>

        {/* Botões de Ação */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm"
          >
            {showDetails ? 'Ocultar' : 'Detalhes'}
          </button>
          <button
            onClick={() => onSelect && onSelect(exercise)}
            className={`px-4 py-2 rounded font-medium text-sm transition-colors ${
              isSelected
                ? 'bg-green-500 hover:bg-green-600 text-white'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {isSelected ? '✅ Selecionado' : '➕ Adicionar'}
          </button>
        </div>
      </div>

      {/* Detalhes Expandidos */}
      {showDetails && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <ExerciseDetails exercise={exercise} />
        </div>
      )}
    </div>
  );
};

// Componente de Detalhes do Exercício
const ExerciseDetails = ({ exercise }) => {
  return (
    <div className="space-y-4">
      {/* Instruções */}
      <div>
        <h4 className="font-medium text-gray-900 mb-2">📋 Como Executar:</h4>
        <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
          {exercise.instrucoes.map((instrucao, index) => (
            <li key={index}>{instrucao}</li>
          ))}
        </ol>
      </div>

      {/* Dicas */}
      <div>
        <h4 className="font-medium text-gray-900 mb-2">💡 Dicas Importantes:</h4>
        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
          {exercise.dicas.map((dica, index) => (
            <li key={index}>{dica}</li>
          ))}
        </ul>
      </div>

      {/* Músculos Secundários */}
      {exercise.musculos_secundarios.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2">🎯 Músculos Secundários:</h4>
          <div className="flex flex-wrap gap-1">
            {exercise.musculos_secundarios.map((muscle, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
              >
                {muscle.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExerciseLibrary;


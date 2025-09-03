import React, { useState, useEffect } from 'react';
import FoodSearch from './FoodSearch';
import { useNutrition } from '../../hooks/useNutrition';

const MealPlanner = ({ userProfile }) => {
  const [selectedMeal, setSelectedMeal] = useState('cafe_manha');
  const [showFoodSearch, setShowFoodSearch] = useState(false);
  const [planName, setPlanName] = useState('');
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  
  // Hook de nutrição integrado com Firebase
  const {
    currentDayIntake,
    loading,
    error,
    saveMealPlan,
    addFoodToMeal,
    removeFoodFromMeal,
    getDayProgress
  } = useNutrition();

  // Estado local das refeições (sincronizado com Firebase)
  const [mealFoods, setMealFoods] = useState({
    cafe_manha: [],
    lanche_manha: [],
    almoco: [],
    lanche_tarde: [],
    jantar: [],
    ceia: []
  });

  // Sincroniza com dados do Firebase quando carregados
  useEffect(() => {
    if (currentDayIntake?.meals) {
      setMealFoods(currentDayIntake.meals);
    }
  }, [currentDayIntake]);

  const mealTypes = [
    { id: 'cafe_manha', nome: 'Café da Manhã', icon: '🌅', time: '07:00' },
    { id: 'lanche_manha', nome: 'Lanche da Manhã', icon: '☕', time: '10:00' },
    { id: 'almoco', nome: 'Almoço', icon: '🍽️', time: '12:30' },
    { id: 'lanche_tarde', nome: 'Lanche da Tarde', icon: '🥪', time: '15:30' },
    { id: 'jantar', nome: 'Jantar', icon: '🌙', time: '19:00' },
    { id: 'ceia', nome: 'Ceia', icon: '🌜', time: '22:00' }
  ];

  const handleFoodAdd = async (food) => {
    // Adiciona localmente para feedback imediato
    setMealFoods(prev => ({
      ...prev,
      [selectedMeal]: [...prev[selectedMeal], { ...food, id: Date.now() }]
    }));
    
    // Salva no Firebase
    const result = await addFoodToMeal(selectedMeal, food);
    if (!result.success) {
      console.error('Erro ao salvar no Firebase:', result.error);
      // Reverte mudança local em caso de erro
      setMealFoods(prev => ({
        ...prev,
        [selectedMeal]: prev[selectedMeal].slice(0, -1)
      }));
    }
    
    setShowFoodSearch(false);
  };

  const handleFoodRemove = async (mealType, foodIndex) => {
    // Remove localmente para feedback imediato
    const originalFoods = mealFoods[mealType];
    setMealFoods(prev => ({
      ...prev,
      [mealType]: prev[mealType].filter((_, index) => index !== foodIndex)
    }));
    
    // Remove do Firebase
    const result = await removeFoodFromMeal(mealType, foodIndex);
    if (!result.success) {
      console.error('Erro ao remover do Firebase:', result.error);
      // Reverte mudança local em caso de erro
      setMealFoods(prev => ({
        ...prev,
        [mealType]: originalFoods
      }));
    }
  };

  const handleSavePlan = async () => {
    if (!planName.trim()) {
      alert('Por favor, digite um nome para o plano');
      return;
    }
    
    const result = await saveMealPlan(mealFoods, planName);
    if (result.success) {
      alert('Plano salvo com sucesso!');
      setShowSaveDialog(false);
      setPlanName('');
    } else {
      alert('Erro ao salvar plano: ' + result.error);
    }
  };

  const calculateMealNutrition = (foods) => {
    return foods.reduce((total, food) => ({
      energia_kcal: total.energia_kcal + (food.energia_kcal || 0),
      proteina_g: total.proteina_g + (food.proteina_g || 0),
      carboidrato_g: total.carboidrato_g + (food.carboidrato_g || 0),
      lipidios_g: total.lipidios_g + (food.lipidios_g || 0),
      fibra_g: total.fibra_g + (food.fibra_g || 0)
    }), {
      energia_kcal: 0,
      proteina_g: 0,
      carboidrato_g: 0,
      lipidios_g: 0,
      fibra_g: 0
    });
  };

  const calculateDayTotals = () => {
    const allFoods = Object.values(mealFoods).flat();
    return calculateMealNutrition(allFoods);
  };

  const dayTotals = currentDayIntake?.nutritionSummary || calculateDayTotals();
  const dayProgress = getDayProgress();
  const targetCalories = userProfile?.calculatedResults?.targetCalories || dayProgress?.calories?.goal || 2000;
  const targetProtein = userProfile?.calculatedResults?.macros?.protein?.grams || dayProgress?.protein?.goal || 150;

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-center">
        <div className="text-2xl">⏳</div>
        <p>Carregando dados nutricionais...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Planejador de Refeições</h2>
        <p className="text-gray-600">Monte seu cardápio diário com alimentos da base TACO</p>
      </div>

      {/* Resumo Nutricional do Dia */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white">
        <h3 className="text-lg font-semibold mb-4">Resumo Nutricional do Dia</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{Math.round(dayTotals.energia_kcal)}</div>
            <div className="text-sm opacity-90">kcal</div>
            <div className="text-xs opacity-75">Meta: {targetCalories}</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{Math.round(dayTotals.proteina_g)}g</div>
            <div className="text-sm opacity-90">Proteína</div>
            <div className="text-xs opacity-75">Meta: {targetProtein}g</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{Math.round(dayTotals.carboidrato_g)}g</div>
            <div className="text-sm opacity-90">Carboidratos</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{Math.round(dayTotals.lipidios_g)}g</div>
            <div className="text-sm opacity-90">Gorduras</div>
          </div>
        </div>
      </div>

      {/* Seletor de Refeições */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
        {mealTypes.map((meal) => (
          <button
            key={meal.id}
            onClick={() => setSelectedMeal(meal.id)}
            className={`p-3 rounded-lg text-center transition-colors ${
              selectedMeal === meal.id
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
            }`}
          >
            <div className="text-2xl mb-1">{meal.icon}</div>
            <div className="text-xs font-medium">{meal.nome}</div>
            <div className="text-xs opacity-75">{meal.time}</div>
          </button>
        ))}
      </div>

      {/* Refeição Selecionada */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold text-gray-900">
            {mealTypes.find(m => m.id === selectedMeal)?.nome}
          </h3>
          <button
            onClick={() => setShowFoodSearch(!showFoodSearch)}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium"
          >
            {showFoodSearch ? 'Fechar Busca' : '+ Adicionar Alimento'}
          </button>
        </div>

        {/* Busca de Alimentos */}
        {showFoodSearch && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <FoodSearch
              onFoodSelect={handleFoodAdd}
              selectedFoods={mealFoods[selectedMeal]}
            />
          </div>
        )}

        {/* Alimentos da Refeição */}
        <div className="space-y-3">
          {mealFoods[selectedMeal].length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">🍽️</div>
              <p>Nenhum alimento adicionado</p>
              <p className="text-sm">Clique em "Adicionar Alimento" para começar</p>
            </div>
          ) : (
            mealFoods[selectedMeal].map((food, index) => (
              <MealFoodItem
                key={index}
                food={food}
                onRemove={() => handleFoodRemove(selectedMeal, index)}
              />
            ))
          )}
        </div>

        {/* Resumo da Refeição */}
        {mealFoods[selectedMeal].length > 0 && (
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Resumo da Refeição</h4>
            <div className="grid grid-cols-4 gap-4 text-center">
              {(() => {
                const nutrition = calculateMealNutrition(mealFoods[selectedMeal]);
                return (
                  <>
                    <div>
                      <div className="font-semibold text-orange-600">{Math.round(nutrition.energia_kcal)}</div>
                      <div className="text-sm text-gray-600">kcal</div>
                    </div>
                    <div>
                      <div className="font-semibold text-blue-600">{Math.round(nutrition.proteina_g)}g</div>
                      <div className="text-sm text-gray-600">Proteína</div>
                    </div>
                    <div>
                      <div className="font-semibold text-green-600">{Math.round(nutrition.carboidrato_g)}g</div>
                      <div className="text-sm text-gray-600">Carboidratos</div>
                    </div>
                    <div>
                      <div className="font-semibold text-purple-600">{Math.round(nutrition.lipidios_g)}g</div>
                      <div className="text-sm text-gray-600">Gorduras</div>
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        )}
      </div>

      {/* Botões de Ação */}
      <div className="flex justify-center gap-4">
        <button
          onClick={() => setShowSaveDialog(true)}
          className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-semibold"
        >
          💾 Salvar como Plano
        </button>
        
        <button
          onClick={() => window.location.reload()}
          className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold"
        >
          🔄 Atualizar Dados
        </button>
      </div>

      {/* Dialog para Salvar Plano */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Salvar Plano Alimentar</h3>
            
            <input
              type="text"
              placeholder="Nome do plano (ex: Dieta Ganho de Massa)"
              value={planName}
              onChange={(e) => setPlanName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"
            />
            
            <div className="flex gap-3">
              <button
                onClick={handleSavePlan}
                disabled={!planName.trim()}
                className="flex-1 bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white py-2 rounded-lg font-medium"
              >
                Salvar
              </button>
              <button
                onClick={() => {
                  setShowSaveDialog(false);
                  setPlanName('');
                }}
                className="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-2 rounded-lg font-medium"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Mensagem de Erro */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
          <strong>Erro:</strong> {error}
        </div>
      )}
    </div>
  );
};

const MealFoodItem = ({ food, onRemove }) => {
  return (
    <div className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg">
      <div className="flex-1">
        <h4 className="font-medium text-gray-900">{food.nome}</h4>
        <p className="text-sm text-gray-500">
          {food.selectedQuantity || food.quantidade_g}g • {food.selectedMeasure || 'gramas'}
        </p>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="grid grid-cols-4 gap-2 text-xs text-center">
          <div>
            <div className="font-semibold text-orange-600">{food.energia_kcal}</div>
            <div className="text-gray-500">kcal</div>
          </div>
          <div>
            <div className="font-semibold text-blue-600">{food.proteina_g}g</div>
            <div className="text-gray-500">Prot</div>
          </div>
          <div>
            <div className="font-semibold text-green-600">{food.carboidrato_g}g</div>
            <div className="text-gray-500">Carb</div>
          </div>
          <div>
            <div className="font-semibold text-purple-600">{food.lipidios_g}g</div>
            <div className="text-gray-500">Gord</div>
          </div>
        </div>
        
        <button
          onClick={onRemove}
          className="text-red-500 hover:text-red-700 p-1"
        >
          🗑️
        </button>
      </div>
    </div>
  );
};

export default MealPlanner;


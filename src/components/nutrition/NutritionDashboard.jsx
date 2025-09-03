import React, { useState } from 'react';
import { useNutrition } from '../../hooks/useNutrition';
import MealPlanner from './MealPlanner';

const NutritionDashboard = ({ userProfile }) => {
  const [activeTab, setActiveTab] = useState('today');
  
  const {
    currentDayIntake,
    intakeHistory,
    mealPlans,
    favoriteFoods,
    suggestions,
    loading,
    error,
    getDayProgress,
    getWeekStats
  } = useNutrition();

  const dayProgress = getDayProgress();
  const weekStats = getWeekStats();

  const tabs = [
    { id: 'today', name: 'Hoje', icon: '📅' },
    { id: 'planner', name: 'Planejador', icon: '🍽️' },
    { id: 'history', name: 'Histórico', icon: '📊' },
    { id: 'plans', name: 'Meus Planos', icon: '📋' },
    { id: 'favorites', name: 'Favoritos', icon: '⭐' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-gray-600">Carregando dados nutricionais...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Nutrição EvolveYou</h1>
        <p className="text-gray-600">Acompanhe sua alimentação com dados precisos da base TACO</p>
      </div>

      {/* Navegação */}
      <div className="flex flex-wrap justify-center gap-2 mb-8">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
            }`}
          >
            {tab.icon} {tab.name}
          </button>
        ))}
      </div>

      {/* Conteúdo das Abas */}
      {activeTab === 'today' && (
        <TodayTab 
          currentDayIntake={currentDayIntake}
          dayProgress={dayProgress}
          suggestions={suggestions}
          userProfile={userProfile}
        />
      )}

      {activeTab === 'planner' && (
        <MealPlanner userProfile={userProfile} />
      )}

      {activeTab === 'history' && (
        <HistoryTab 
          intakeHistory={intakeHistory}
          weekStats={weekStats}
        />
      )}

      {activeTab === 'plans' && (
        <PlansTab mealPlans={mealPlans} />
      )}

      {activeTab === 'favorites' && (
        <FavoritesTab favoriteFoods={favoriteFoods} />
      )}

      {/* Mensagem de Erro */}
      {error && (
        <div className="mt-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
          <strong>Erro:</strong> {error}
        </div>
      )}
    </div>
  );
};

// Aba Hoje
const TodayTab = ({ currentDayIntake, dayProgress, suggestions, userProfile }) => {
  const nutrition = currentDayIntake?.nutritionSummary || {
    energia_kcal: 0,
    proteina_g: 0,
    carboidrato_g: 0,
    lipidios_g: 0
  };

  const goals = {
    energia_kcal: userProfile?.calculatedResults?.targetCalories || dayProgress?.calories?.goal || 2000,
    proteina_g: userProfile?.calculatedResults?.macros?.protein?.grams || dayProgress?.protein?.goal || 150,
    carboidrato_g: userProfile?.calculatedResults?.macros?.carbs?.grams || 250,
    lipidios_g: userProfile?.calculatedResults?.macros?.fat?.grams || 67
  };

  return (
    <div className="space-y-6">
      {/* Resumo do Dia */}
      <div className="bg-gradient-to-r from-green-500 to-blue-600 rounded-xl p-6 text-white">
        <h2 className="text-xl font-semibold mb-4">Resumo de Hoje</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{Math.round(nutrition.energia_kcal)}</div>
            <div className="text-sm opacity-90">kcal consumidas</div>
            <div className="text-xs opacity-75">Meta: {goals.energia_kcal}</div>
            <div className="w-full bg-white bg-opacity-20 rounded-full h-2 mt-2">
              <div 
                className="bg-white h-2 rounded-full transition-all"
                style={{ width: `${Math.min((nutrition.energia_kcal / goals.energia_kcal) * 100, 100)}%` }}
              />
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold">{Math.round(nutrition.proteina_g)}g</div>
            <div className="text-sm opacity-90">Proteína</div>
            <div className="text-xs opacity-75">Meta: {goals.proteina_g}g</div>
            <div className="w-full bg-white bg-opacity-20 rounded-full h-2 mt-2">
              <div 
                className="bg-white h-2 rounded-full transition-all"
                style={{ width: `${Math.min((nutrition.proteina_g / goals.proteina_g) * 100, 100)}%` }}
              />
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold">{Math.round(nutrition.carboidrato_g)}g</div>
            <div className="text-sm opacity-90">Carboidratos</div>
            <div className="text-xs opacity-75">Meta: {goals.carboidrato_g}g</div>
            <div className="w-full bg-white bg-opacity-20 rounded-full h-2 mt-2">
              <div 
                className="bg-white h-2 rounded-full transition-all"
                style={{ width: `${Math.min((nutrition.carboidrato_g / goals.carboidrato_g) * 100, 100)}%` }}
              />
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold">{Math.round(nutrition.lipidios_g)}g</div>
            <div className="text-sm opacity-90">Gorduras</div>
            <div className="text-xs opacity-75">Meta: {goals.lipidios_g}g</div>
            <div className="w-full bg-white bg-opacity-20 rounded-full h-2 mt-2">
              <div 
                className="bg-white h-2 rounded-full transition-all"
                style={{ width: `${Math.min((nutrition.lipidios_g / goals.lipidios_g) * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Refeições do Dia */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Refeições de Hoje</h3>
        
        {currentDayIntake?.meals ? (
          <div className="space-y-4">
            {Object.entries(currentDayIntake.meals).map(([mealType, foods]) => (
              <MealSummary key={mealType} mealType={mealType} foods={foods} />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🍽️</div>
            <p>Nenhuma refeição registrada hoje</p>
            <p className="text-sm">Use o Planejador para adicionar alimentos</p>
          </div>
        )}
      </div>

      {/* Sugestões */}
      {suggestions.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-yellow-800 mb-4">💡 Sugestões Personalizadas</h3>
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="text-yellow-700">
                • {suggestion.message}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Componente de Resumo de Refeição
const MealSummary = ({ mealType, foods }) => {
  const mealNames = {
    cafe_manha: 'Café da Manhã',
    lanche_manha: 'Lanche da Manhã',
    almoco: 'Almoço',
    lanche_tarde: 'Lanche da Tarde',
    jantar: 'Jantar',
    ceia: 'Ceia'
  };

  const totalCalories = foods.reduce((sum, food) => sum + (food.energia_kcal || 0), 0);

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="flex justify-between items-center mb-2">
        <h4 className="font-medium text-gray-900">{mealNames[mealType]}</h4>
        <span className="text-sm font-semibold text-orange-600">{Math.round(totalCalories)} kcal</span>
      </div>
      
      {foods.length > 0 ? (
        <div className="space-y-1">
          {foods.map((food, index) => (
            <div key={index} className="text-sm text-gray-600 flex justify-between">
              <span>{food.nome}</span>
              <span>{food.energia_kcal} kcal</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-500">Nenhum alimento adicionado</p>
      )}
    </div>
  );
};

// Aba Histórico
const HistoryTab = ({ intakeHistory, weekStats }) => {
  return (
    <div className="space-y-6">
      {/* Estatísticas da Semana */}
      {weekStats && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Estatísticas da Semana</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{weekStats.avgCalories}</div>
              <div className="text-sm text-gray-600">Média de Calorias</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{weekStats.avgProtein}g</div>
              <div className="text-sm text-gray-600">Média de Proteína</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{weekStats.daysTracked}</div>
              <div className="text-sm text-gray-600">Dias Registrados</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{weekStats.consistency}%</div>
              <div className="text-sm text-gray-600">Consistência</div>
            </div>
          </div>
        </div>
      )}

      {/* Histórico Diário */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Histórico dos Últimos Dias</h3>
        
        {intakeHistory.length > 0 ? (
          <div className="space-y-3">
            {intakeHistory.map((day) => (
              <div key={day.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <span className="font-medium">{new Date(day.date).toLocaleDateString('pt-BR')}</span>
                  <span className="text-orange-600 font-semibold">
                    {Math.round(day.nutritionSummary.energia_kcal)} kcal
                  </span>
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  Proteína: {Math.round(day.nutritionSummary.proteina_g)}g • 
                  Carbs: {Math.round(day.nutritionSummary.carboidrato_g)}g • 
                  Gordura: {Math.round(day.nutritionSummary.lipidios_g)}g
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">📊</div>
            <p>Nenhum histórico encontrado</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Aba Planos
const PlansTab = ({ mealPlans }) => {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Meus Planos Alimentares</h3>
      
      {mealPlans.length > 0 ? (
        <div className="grid gap-4">
          {mealPlans.map((plan) => (
            <div key={plan.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-medium text-gray-900">{plan.planName}</h4>
                  <p className="text-sm text-gray-600">
                    Criado em {new Date(plan.createdAt?.toDate()).toLocaleDateString('pt-BR')}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-orange-600">
                    {Math.round(plan.nutritionSummary.energia_kcal)} kcal
                  </div>
                  <div className="text-sm text-gray-600">
                    {Math.round(plan.nutritionSummary.proteina_g)}g proteína
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">📋</div>
          <p>Nenhum plano salvo</p>
          <p className="text-sm">Use o Planejador para criar seus planos</p>
        </div>
      )}
    </div>
  );
};

// Aba Favoritos
const FavoritesTab = ({ favoriteFoods }) => {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Alimentos Favoritos</h3>
      
      {favoriteFoods.length > 0 ? (
        <div className="grid gap-3">
          {favoriteFoods.map((favorite) => (
            <div key={favorite.id} className="border border-gray-200 rounded-lg p-3">
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-medium text-gray-900">{favorite.foodData.nome}</h4>
                  <p className="text-sm text-gray-600 capitalize">
                    {favorite.foodData.categoria.replace('_', ' ')}
                  </p>
                </div>
                <div className="text-right text-sm">
                  <div className="font-semibold text-orange-600">
                    {favorite.foodData.energia_kcal} kcal/100g
                  </div>
                  <div className="text-gray-600">
                    {favorite.foodData.proteina_g}g proteína
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">⭐</div>
          <p>Nenhum favorito adicionado</p>
          <p className="text-sm">Adicione alimentos aos favoritos durante a busca</p>
        </div>
      )}
    </div>
  );
};

export default NutritionDashboard;


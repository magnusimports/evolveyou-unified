import React, { useState, useEffect } from 'react';
import { searchFoods, getFoodsByCategory, foodCategories, calculateNutrition } from '../../data/tacoDatabase';

const FoodSearch = ({ onFoodSelect, selectedFoods = [] }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    if (searchQuery.length >= 2) {
      const results = searchFoods(searchQuery);
      setSearchResults(results.slice(0, 10)); // Limitar a 10 resultados
      setShowResults(true);
    } else if (selectedCategory) {
      const results = getFoodsByCategory(selectedCategory);
      setSearchResults(results.slice(0, 15));
      setShowResults(true);
    } else {
      setSearchResults([]);
      setShowResults(false);
    }
  }, [searchQuery, selectedCategory]);

  const handleFoodSelect = (food, quantity = 100) => {
    const nutritionData = calculateNutrition(food.id, quantity);
    onFoodSelect({
      ...nutritionData,
      selectedQuantity: quantity,
      selectedMeasure: 'gramas'
    });
    setSearchQuery('');
    setShowResults(false);
  };

  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId === selectedCategory ? '' : categoryId);
    setSearchQuery('');
  };

  return (
    <div className="space-y-4">
      {/* Barra de Busca */}
      <div className="relative">
        <input
          type="text"
          placeholder="Buscar alimentos (ex: frango, arroz, banana...)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {searchQuery && (
          <button
            onClick={() => {
              setSearchQuery('');
              setShowResults(false);
            }}
            className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        )}
      </div>

      {/* Categorias */}
      <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
        {foodCategories.map((category) => (
          <button
            key={category.id}
            onClick={() => handleCategorySelect(category.id)}
            className={`p-3 rounded-lg text-center transition-colors ${
              selectedCategory === category.id
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
            }`}
          >
            <div className="text-2xl mb-1">{category.icon}</div>
            <div className="text-xs font-medium">{category.nome.split(' ')[0]}</div>
          </button>
        ))}
      </div>

      {/* Resultados da Busca */}
      {showResults && searchResults.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg max-h-96 overflow-y-auto">
          <div className="p-3 border-b border-gray-200 bg-gray-50">
            <h3 className="font-semibold text-gray-800">
              {searchQuery ? `Resultados para "${searchQuery}"` : `Categoria: ${foodCategories.find(c => c.id === selectedCategory)?.nome}`}
            </h3>
          </div>
          
          <div className="divide-y divide-gray-100">
            {searchResults.map((food) => (
              <FoodItem
                key={food.id}
                food={food}
                onSelect={handleFoodSelect}
                isSelected={selectedFoods.some(f => f.id === food.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Sem Resultados */}
      {showResults && searchResults.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">🔍</div>
          <p>Nenhum alimento encontrado</p>
          <p className="text-sm">Tente buscar por outro termo</p>
        </div>
      )}
    </div>
  );
};

const FoodItem = ({ food, onSelect, isSelected }) => {
  const [quantity, setQuantity] = useState(100);
  const [selectedMeasure, setSelectedMeasure] = useState('gramas');

  const handleQuantityChange = (value) => {
    setQuantity(Math.max(1, parseInt(value) || 1));
  };

  const handleMeasureChange = (measure) => {
    setSelectedMeasure(measure);
    if (measure !== 'gramas') {
      const measureData = food.medidas_caseiras.find(m => m.nome === measure);
      if (measureData) {
        setQuantity(measureData.peso_g);
      }
    }
  };

  const nutritionPreview = calculateNutrition(food.id, quantity);

  return (
    <div className={`p-4 hover:bg-gray-50 ${isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : ''}`}>
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900">{food.nome}</h4>
          <p className="text-sm text-gray-500 capitalize">
            {food.categoria.replace('_', ' ')} • {food.grupo.replace('_', ' ')}
          </p>
        </div>
        
        {isSelected && (
          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
            Adicionado
          </span>
        )}
      </div>

      {/* Informações Nutricionais */}
      <div className="grid grid-cols-4 gap-2 mb-3 text-xs">
        <div className="text-center">
          <div className="font-semibold text-orange-600">{nutritionPreview?.energia_kcal}</div>
          <div className="text-gray-500">kcal</div>
        </div>
        <div className="text-center">
          <div className="font-semibold text-blue-600">{nutritionPreview?.proteina_g}g</div>
          <div className="text-gray-500">Prot</div>
        </div>
        <div className="text-center">
          <div className="font-semibold text-green-600">{nutritionPreview?.carboidrato_g}g</div>
          <div className="text-gray-500">Carb</div>
        </div>
        <div className="text-center">
          <div className="font-semibold text-purple-600">{nutritionPreview?.lipidios_g}g</div>
          <div className="text-gray-500">Gord</div>
        </div>
      </div>

      {/* Controles de Quantidade */}
      <div className="flex items-center gap-2 mb-3">
        <input
          type="number"
          value={quantity}
          onChange={(e) => handleQuantityChange(e.target.value)}
          className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
          min="1"
        />
        
        <select
          value={selectedMeasure}
          onChange={(e) => handleMeasureChange(e.target.value)}
          className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
        >
          <option value="gramas">gramas</option>
          {food.medidas_caseiras.map((measure) => (
            <option key={measure.nome} value={measure.nome}>
              {measure.nome} ({measure.peso_g}g)
            </option>
          ))}
        </select>
      </div>

      {/* Botão Adicionar */}
      <button
        onClick={() => onSelect(food, quantity)}
        disabled={isSelected}
        className={`w-full py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
          isSelected
            ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
            : 'bg-blue-500 hover:bg-blue-600 text-white'
        }`}
      >
        {isSelected ? 'Já Adicionado' : 'Adicionar Alimento'}
      </button>
    </div>
  );
};

export default FoodSearch;


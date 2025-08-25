/**
 * Gerenciador de banco de dados para alimentos TBCA
 * EvolveYou Backend - Content Service
 */

const fs = require('fs').promises;
const path = require('path');
const Food = require('../models/Food');

class FoodDatabase {
    constructor() {
        this.foods = new Map(); // Cache em memória
        this.groups = new Set();
        this.dataPath = path.join(__dirname, '../../data/foods.json');
        this.isLoaded = false;
    }

    // Carregar dados do arquivo JSON
    async loadData(filePath = null) {
        try {
            const dataFile = filePath || this.dataPath;
            console.log(`Carregando dados de alimentos de: ${dataFile}`);
            
            const data = await fs.readFile(dataFile, 'utf8');
            const foodsData = JSON.parse(data);
            
            // Limpar cache atual
            this.foods.clear();
            this.groups.clear();
            
            // Carregar alimentos
            let loadedCount = 0;
            for (const foodData of foodsData) {
                try {
                    const food = new Food(foodData);
                    const validation = food.validate();
                    
                    if (validation.isValid) {
                        this.foods.set(food.codigo, food);
                        this.groups.add(food.grupo);
                        loadedCount++;
                    } else {
                        console.warn(`Alimento inválido ${food.codigo}: ${validation.errors.join(', ')}`);
                    }
                } catch (error) {
                    console.error(`Erro ao processar alimento:`, error);
                }
            }
            
            this.isLoaded = true;
            console.log(`✅ ${loadedCount} alimentos carregados com sucesso`);
            console.log(`📊 Grupos disponíveis: ${Array.from(this.groups).join(', ')}`);
            
            return loadedCount;
            
        } catch (error) {
            console.error('Erro ao carregar dados de alimentos:', error);
            throw error;
        }
    }

    // Salvar dados no arquivo JSON
    async saveData(filePath = null) {
        try {
            const dataFile = filePath || this.dataPath;
            
            // Criar diretório se não existir
            const dir = path.dirname(dataFile);
            await fs.mkdir(dir, { recursive: true });
            
            // Converter Map para Array
            const foodsArray = Array.from(this.foods.values()).map(food => food.toJSON());
            
            await fs.writeFile(dataFile, JSON.stringify(foodsArray, null, 2), 'utf8');
            console.log(`✅ Dados salvos em: ${dataFile}`);
            
            return true;
        } catch (error) {
            console.error('Erro ao salvar dados:', error);
            throw error;
        }
    }

    // Importar dados da TBCA
    async importTBCAData(tbcaFilePath) {
        try {
            console.log(`Importando dados da TBCA de: ${tbcaFilePath}`);
            
            const data = await fs.readFile(tbcaFilePath, 'utf8');
            const tbcaData = JSON.parse(data);
            
            let importedCount = 0;
            let skippedCount = 0;
            
            for (const foodData of tbcaData) {
                try {
                    const food = new Food(foodData);
                    const validation = food.validate();
                    
                    if (validation.isValid) {
                        this.foods.set(food.codigo, food);
                        this.groups.add(food.grupo);
                        importedCount++;
                    } else {
                        console.warn(`Alimento inválido ${food.codigo}: ${validation.errors.join(', ')}`);
                        skippedCount++;
                    }
                } catch (error) {
                    console.error(`Erro ao processar alimento:`, error);
                    skippedCount++;
                }
            }
            
            this.isLoaded = true;
            
            console.log(`✅ Importação concluída:`);
            console.log(`   - Importados: ${importedCount} alimentos`);
            console.log(`   - Ignorados: ${skippedCount} alimentos`);
            console.log(`   - Grupos: ${Array.from(this.groups).join(', ')}`);
            
            // Salvar dados importados
            await this.saveData();
            
            return { imported: importedCount, skipped: skippedCount };
            
        } catch (error) {
            console.error('Erro ao importar dados da TBCA:', error);
            throw error;
        }
    }

    // Buscar alimento por código
    getFood(codigo) {
        return this.foods.get(codigo);
    }

    // Buscar alimentos por nome (busca parcial)
    searchByName(query, limit = 20) {
        const queryLower = query.toLowerCase();
        const results = [];
        
        for (const food of this.foods.values()) {
            if (food.nome.toLowerCase().includes(queryLower)) {
                results.push(food);
                if (results.length >= limit) break;
            }
        }
        
        return results;
    }

    // Buscar alimentos por grupo
    getByGroup(grupo, limit = 50) {
        const results = [];
        
        for (const food of this.foods.values()) {
            if (food.grupo === grupo) {
                results.push(food);
                if (results.length >= limit) break;
            }
        }
        
        return results;
    }

    // Obter todos os grupos disponíveis
    getGroups() {
        return Array.from(this.groups);
    }

    // Obter estatísticas do banco de dados
    getStats() {
        const stats = {
            total_foods: this.foods.size,
            groups: Array.from(this.groups).length,
            groups_list: Array.from(this.groups),
            foods_by_group: {}
        };
        
        // Contar alimentos por grupo
        for (const food of this.foods.values()) {
            stats.foods_by_group[food.grupo] = (stats.foods_by_group[food.grupo] || 0) + 1;
        }
        
        return stats;
    }

    // Filtrar alimentos por critérios nutricionais
    filterByCriteria(criteria, limit = 50) {
        const allFoods = Array.from(this.foods.values());
        const filtered = Food.filterByCriteria(allFoods, criteria);
        
        return filtered.slice(0, limit);
    }

    // Buscar alimentos similares
    findSimilar(codigo, limit = 5) {
        const targetFood = this.getFood(codigo);
        if (!targetFood) return [];
        
        const allFoods = Array.from(this.foods.values());
        return Food.findSimilar(targetFood, allFoods, limit);
    }

    // Obter alimentos aleatórios
    getRandomFoods(count = 10, grupo = null) {
        let foodsArray;
        
        if (grupo) {
            foodsArray = this.getByGroup(grupo);
        } else {
            foodsArray = Array.from(this.foods.values());
        }
        
        // Embaralhar array
        for (let i = foodsArray.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [foodsArray[i], foodsArray[j]] = [foodsArray[j], foodsArray[i]];
        }
        
        return foodsArray.slice(0, count);
    }

    // Obter alimentos para algoritmo de dieta
    getFoodsForDietAlgorithm(criteria = {}) {
        const foods = this.filterByCriteria(criteria);
        return foods.map(food => food.toAlgorithmFormat());
    }

    // Buscar alimentos ricos em nutriente específico
    getRichInNutrient(nutrient, limit = 20) {
        const allFoods = Array.from(this.foods.values());
        
        // Mapear nomes de nutrientes para métodos
        const nutrientMethods = {
            'proteina': 'getProteinas',
            'carboidrato': 'getCarboidratos',
            'lipidio': 'getLipidios',
            'fibra': 'getFibras',
            'calcio': 'getCalcio',
            'ferro': 'getFerro',
            'vitamina_c': 'getVitaminaC'
        };
        
        const method = nutrientMethods[nutrient.toLowerCase()];
        if (!method) return [];
        
        return allFoods
            .filter(food => food[method]() > 0)
            .sort((a, b) => b[method]() - a[method]())
            .slice(0, limit);
    }

    // Verificar se o banco está carregado
    isReady() {
        return this.isLoaded && this.foods.size > 0;
    }

    // Recarregar dados
    async reload() {
        this.isLoaded = false;
        return await this.loadData();
    }
}

// Singleton instance
let instance = null;

function getFoodDatabase() {
    if (!instance) {
        instance = new FoodDatabase();
    }
    return instance;
}

module.exports = { FoodDatabase, getFoodDatabase };


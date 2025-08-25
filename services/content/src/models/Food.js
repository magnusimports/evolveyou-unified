/**
 * Modelo de dados para alimentos - TBCA
 * EvolveYou Backend - Content Service
 */

class Food {
    constructor(data) {
        this.codigo = data.codigo;
        this.nome = data.nome;
        this.nome_cientifico = data.nome_cientifico || '';
        this.grupo = data.grupo;
        this.composicao = data.composicao || {};
        this.fonte = data.fonte || 'TBCA';
        this.url_fonte = data.url_fonte || '';
        this.created_at = new Date();
        this.updated_at = new Date();
    }

    // Métodos para acessar componentes nutricionais específicos
    getEnergia() {
        return this.getComponente('Energia') || 0;
    }

    getCarboidratos() {
        return this.getComponente('Carboidrato total') || 0;
    }

    getProteinas() {
        return this.getComponente('Proteína') || 0;
    }

    getLipidios() {
        return this.getComponente('Lipídios') || 0;
    }

    getFibras() {
        return this.getComponente('Fibra alimentar') || 0;
    }

    getCalcio() {
        return this.getComponente('Cálcio') || 0;
    }

    getFerro() {
        return this.getComponente('Ferro') || 0;
    }

    getSodio() {
        return this.getComponente('Sódio') || 0;
    }

    getVitaminaC() {
        return this.getComponente('Vitamina C') || 0;
    }

    // Método genérico para obter qualquer componente
    getComponente(nome) {
        const componente = this.composicao[nome];
        return componente ? componente.valor : 0;
    }

    // Método para obter unidade de um componente
    getUnidade(nome) {
        const componente = this.composicao[nome];
        return componente ? componente.unidade : '';
    }

    // Calcular macronutrientes em percentual
    getMacronutrientesPercentual() {
        const carboidratos = this.getCarboidratos();
        const proteinas = this.getProteinas();
        const lipidios = this.getLipidios();
        
        const total = carboidratos + proteinas + lipidios;
        
        if (total === 0) return { carboidratos: 0, proteinas: 0, lipidios: 0 };
        
        return {
            carboidratos: Math.round((carboidratos / total) * 100),
            proteinas: Math.round((proteinas / total) * 100),
            lipidios: Math.round((lipidios / total) * 100)
        };
    }

    // Verificar se é adequado para dietas específicas
    isLowCarb() {
        const macros = this.getMacronutrientesPercentual();
        return macros.carboidratos < 20;
    }

    isHighProtein() {
        const macros = this.getMacronutrientesPercentual();
        return macros.proteinas > 30;
    }

    isLowFat() {
        const macros = this.getMacronutrientesPercentual();
        return macros.lipidios < 10;
    }

    // Calcular densidade nutricional (nutrientes por caloria)
    getDensidadeNutricional() {
        const energia = this.getEnergia();
        if (energia === 0) return 0;
        
        const nutrientesEssenciais = [
            this.getProteinas(),
            this.getFibras(),
            this.getCalcio(),
            this.getFerro(),
            this.getVitaminaC()
        ];
        
        const somanutrientes = nutrientesEssenciais.reduce((sum, val) => sum + val, 0);
        return somanutrientes / energia;
    }

    // Converter para formato JSON para API
    toJSON() {
        return {
            codigo: this.codigo,
            nome: this.nome,
            nome_cientifico: this.nome_cientifico,
            grupo: this.grupo,
            composicao: this.composicao,
            macronutrientes: this.getMacronutrientesPercentual(),
            densidade_nutricional: this.getDensidadeNutricional(),
            fonte: this.fonte,
            created_at: this.created_at,
            updated_at: this.updated_at
        };
    }

    // Converter para formato simplificado para algoritmo de dieta
    toAlgorithmFormat() {
        return {
            id: this.codigo,
            name: this.nome,
            group: this.grupo,
            calories: this.getEnergia(),
            carbs: this.getCarboidratos(),
            protein: this.getProteinas(),
            fat: this.getLipidios(),
            fiber: this.getFibras(),
            calcium: this.getCalcio(),
            iron: this.getFerro(),
            sodium: this.getSodio(),
            vitamin_c: this.getVitaminaC(),
            density: this.getDensidadeNutricional()
        };
    }

    // Validar dados do alimento
    validate() {
        const errors = [];
        
        if (!this.codigo) errors.push('Código é obrigatório');
        if (!this.nome) errors.push('Nome é obrigatório');
        if (!this.grupo) errors.push('Grupo é obrigatório');
        
        // Validar se tem pelo menos energia
        if (this.getEnergia() === 0) {
            errors.push('Valor energético é obrigatório');
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    // Buscar alimentos similares por grupo e composição
    static findSimilar(targetFood, foodList, limit = 5) {
        const targetMacros = targetFood.getMacronutrientesPercentual();
        
        const similarities = foodList
            .filter(food => food.grupo === targetFood.grupo && food.codigo !== targetFood.codigo)
            .map(food => {
                const macros = food.getMacronutrientesPercentual();
                
                // Calcular similaridade baseada em macronutrientes
                const diffCarbs = Math.abs(targetMacros.carboidratos - macros.carboidratos);
                const diffProtein = Math.abs(targetMacros.proteinas - macros.proteinas);
                const diffFat = Math.abs(targetMacros.lipidios - macros.lipidios);
                
                const similarity = 100 - (diffCarbs + diffProtein + diffFat) / 3;
                
                return {
                    food: food,
                    similarity: similarity
                };
            })
            .sort((a, b) => b.similarity - a.similarity)
            .slice(0, limit);
        
        return similarities.map(item => item.food);
    }

    // Filtrar alimentos por critérios nutricionais
    static filterByCriteria(foodList, criteria) {
        return foodList.filter(food => {
            // Filtro por energia
            if (criteria.minCalories && food.getEnergia() < criteria.minCalories) return false;
            if (criteria.maxCalories && food.getEnergia() > criteria.maxCalories) return false;
            
            // Filtro por macronutrientes
            if (criteria.minProtein && food.getProteinas() < criteria.minProtein) return false;
            if (criteria.maxCarbs && food.getCarboidratos() > criteria.maxCarbs) return false;
            if (criteria.maxFat && food.getLipidios() > criteria.maxFat) return false;
            
            // Filtro por grupo
            if (criteria.groups && !criteria.groups.includes(food.grupo)) return false;
            
            // Filtro por dietas específicas
            if (criteria.lowCarb && !food.isLowCarb()) return false;
            if (criteria.highProtein && !food.isHighProtein()) return false;
            if (criteria.lowFat && !food.isLowFat()) return false;
            
            return true;
        });
    }
}

module.exports = Food;


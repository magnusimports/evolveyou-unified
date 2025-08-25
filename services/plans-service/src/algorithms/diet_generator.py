"""
Algoritmo de Geração de Dieta Personalizada
"""

import random
import math
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
import structlog
from dataclasses import dataclass

from models.plan import (
    DietPlan, Meal, FoodItem, MealType, GoalType,
    DietPreferences, AlgorithmConfig
)
from config.settings import get_settings
from adapters.taco_data_adapter import TacoDataAdapter

logger = structlog.get_logger(__name__)

@dataclass
class NutritionalTarget:
    """Alvo nutricional para uma refeição"""
    calories: float
    protein: float
    carbs: float
    fat: float
    tolerance: float = 0.1  # ±10% de tolerância

@dataclass
class FoodCandidate:
    """Candidato a alimento para uma refeição"""
    food_id: str
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    category: str
    preparation_time: int
    cost_level: str
    availability_score: float
    preference_score: float

class DietGenerator:
    """Gerador de planos de dieta personalizados"""
    
    def __init__(self, content_service, firebase_service):
        self.content_service = content_service
        self.firebase_service = firebase_service
        self.settings = get_settings()
        self.diet_config = self.settings.diet_algorithm_config
        self.taco_adapter = TacoDataAdapter()
        
    async def generate_diet_plan(
        self, 
        user_id: str, 
        target_date: date,
        algorithm_config: AlgorithmConfig
    ) -> DietPlan:
        """
        Gera um plano de dieta personalizado para o usuário
        
        Args:
            user_id: ID do usuário
            target_date: Data alvo para o plano
            algorithm_config: Configuração do algoritmo
            
        Returns:
            DietPlan: Plano de dieta completo
        """
        logger.info("Iniciando geração de plano de dieta", 
                   user_id=user_id, date=target_date)
        
        try:
            # 1. Verificar se já existe plano para a data
            existing_plan = await self._get_existing_plan(user_id, target_date)
            if existing_plan and not self._should_regenerate_plan(existing_plan, algorithm_config):
                logger.info("Plano existente encontrado", user_id=user_id)
                return existing_plan
            
            # 2. Obter dados do usuário e preferências
            user_data = await self._get_user_data(user_id)
            diet_preferences = algorithm_config.diet_preferences
            
            # 3. Calcular distribuição calórica por refeição
            meal_targets = self._calculate_meal_targets(algorithm_config)
            
            # 4. Obter alimentos disponíveis do Content Service
            available_foods = await self._get_available_foods(diet_preferences)
            
            # 5. Gerar refeições
            meals = []
            for meal_type, target in meal_targets.items():
                meal = await self._generate_meal(
                    meal_type, target, available_foods, 
                    diet_preferences, user_data
                )
                meals.append(meal)
            
            # 6. Calcular totais do plano
            total_calories, total_protein, total_carbs, total_fat = self._calculate_totals(meals)
            
            # 7. Ajustar se necessário
            if self._needs_adjustment(total_calories, algorithm_config.target_calories):
                meals = await self._adjust_plan(meals, algorithm_config, available_foods)
                total_calories, total_protein, total_carbs, total_fat = self._calculate_totals(meals)
            
            # 8. Criar plano final
            diet_plan = DietPlan(
                user_id=user_id,
                date=target_date,
                goal=algorithm_config.goal,
                target_calories=algorithm_config.target_calories,
                target_protein=algorithm_config.target_protein,
                target_carbs=algorithm_config.target_carbs,
                target_fat=algorithm_config.target_fat,
                meals=meals,
                total_calories=total_calories,
                total_protein=total_protein,
                total_carbs=total_carbs,
                total_fat=total_fat,
                water_intake_ml=self._calculate_water_intake(algorithm_config),
                notes=self._generate_diet_notes(algorithm_config, diet_preferences)
            )
            
            # 9. Salvar no Firestore
            await self._save_diet_plan(diet_plan)
            
            logger.info("Plano de dieta gerado com sucesso", 
                       user_id=user_id, total_calories=total_calories)
            
            return diet_plan
            
        except Exception as e:
            logger.error("Erro ao gerar plano de dieta", 
                        user_id=user_id, error=str(e))
            raise
    
    def _calculate_meal_targets(self, config: AlgorithmConfig) -> Dict[MealType, NutritionalTarget]:
        """Calcula alvos nutricionais para cada refeição"""
        meal_distribution = self.diet_config["meal_distribution"]
        macro_distribution = self.diet_config["macro_distribution"]
        tolerance = self.diet_config["tolerance"]
        
        targets = {}
        
        for meal_name, calorie_percentage in meal_distribution.items():
            meal_type = MealType(meal_name)
            meal_calories = config.target_calories * calorie_percentage
            
            # Obter distribuição de macros para esta refeição
            macro_dist = macro_distribution[meal_name]
            
            # Calcular macros em gramas
            protein_calories = meal_calories * macro_dist["protein"]
            carbs_calories = meal_calories * macro_dist["carbs"]
            fat_calories = meal_calories * macro_dist["fat"]
            
            protein_grams = protein_calories / 4  # 4 cal/g
            carbs_grams = carbs_calories / 4      # 4 cal/g
            fat_grams = fat_calories / 9          # 9 cal/g
            
            targets[meal_type] = NutritionalTarget(
                calories=meal_calories,
                protein=protein_grams,
                carbs=carbs_grams,
                fat=fat_grams,
                tolerance=tolerance["calories"]
            )
        
        return targets
    
    async def _get_available_foods(self, preferences: DietPreferences) -> List[FoodCandidate]:
        """Obtém alimentos disponíveis do Content Service usando adaptador TACO"""
        try:
            # Buscar todos os alimentos da Base TACO
            foods_response = await self.content_service.search_foods("")
            taco_foods = foods_response.get("data", [])
            
            logger.info("Alimentos obtidos da Base TACO", count=len(taco_foods))
            
            # Converter dados da TACO para formato esperado
            converted_foods = self.taco_adapter.convert_foods_from_taco(taco_foods)
            
            candidates = []
            for food in converted_foods:
                # Filtrar por restrições dietéticas
                if self._food_matches_restrictions(food, preferences):
                    candidate = FoodCandidate(
                        food_id=food["id"],
                        name=food["name"],
                        calories_per_100g=food["nutrition"]["calories"],
                        protein_per_100g=food["nutrition"]["protein"],
                        carbs_per_100g=food["nutrition"]["carbs"],
                        fat_per_100g=food["nutrition"]["fat"],
                        category=food.get("category", "outros"),
                        preparation_time=food.get("preparation_time", 15),
                        cost_level=food.get("cost_level", "medium"),
                        availability_score=food.get("availability_score", 0.8),
                        preference_score=self._calculate_preference_score(food, preferences)
                    )
                    candidates.append(candidate)
            
            # Ordenar por score de preferência
            candidates.sort(key=lambda x: x.preference_score, reverse=True)
            
            logger.info("Alimentos disponíveis processados", 
                       taco_count=len(taco_foods),
                       converted_count=len(converted_foods),
                       candidates_count=len(candidates))
            return candidates
            
        except Exception as e:
            logger.error("Erro ao obter alimentos da Base TACO", error=str(e))
            raise
    
    def _food_matches_restrictions(self, food: dict, preferences: DietPreferences) -> bool:
        """Verifica se o alimento atende às restrições dietéticas"""
        # Verificar alergias
        for allergy in preferences.allergies:
            if allergy.lower() in food.get("allergens", []):
                return False
        
        # Verificar restrições dietéticas
        food_tags = food.get("dietary_tags", [])
        for restriction in preferences.dietary_restrictions:
            if restriction == "vegetarian" and "meat" in food_tags:
                return False
            elif restriction == "vegan" and ("meat" in food_tags or "dairy" in food_tags):
                return False
            elif restriction == "gluten_free" and "gluten" in food_tags:
                return False
            elif restriction == "lactose_free" and "lactose" in food_tags:
                return False
        
        # Verificar alimentos não desejados
        if food["name"].lower() in [disliked.lower() for disliked in preferences.disliked_foods]:
            return False
        
        return True
    
    def _calculate_preference_score(self, food: dict, preferences: DietPreferences) -> float:
        """Calcula score de preferência para um alimento"""
        score = 0.5  # Score base
        
        # Bonus por alimentos preferidos
        if food["name"].lower() in [preferred.lower() for preferred in preferences.preferred_foods]:
            score += 0.3
        
        # Bonus por tempo de preparo
        prep_time = food.get("preparation_time", 15)
        if preferences.cooking_time_preference == "quick" and prep_time <= 15:
            score += 0.1
        elif preferences.cooking_time_preference == "medium" and 15 < prep_time <= 45:
            score += 0.1
        elif preferences.cooking_time_preference == "elaborate" and prep_time > 45:
            score += 0.1
        
        # Bonus por nível de custo
        cost_level = food.get("cost_level", "medium")
        if cost_level == preferences.budget_level:
            score += 0.1
        
        # Penalty por baixa disponibilidade
        availability = food.get("availability_score", 0.8)
        score *= availability
        
        return min(score, 1.0)
    
    async def _generate_meal(
        self, 
        meal_type: MealType, 
        target: NutritionalTarget,
        available_foods: List[FoodCandidate],
        preferences: DietPreferences,
        user_data: dict
    ) -> Meal:
        """Gera uma refeição específica"""
        
        # Filtrar alimentos apropriados para esta refeição
        suitable_foods = self._filter_foods_for_meal(meal_type, available_foods)
        
        # Algoritmo de montagem da refeição
        # 1. Priorizar proteína
        protein_foods = [f for f in suitable_foods if f.protein_per_100g >= 15]
        selected_foods = []
        
        # Selecionar fonte principal de proteína
        if protein_foods:
            protein_source = self._select_food_by_priority(protein_foods, target.protein, "protein")
            if protein_source:
                selected_foods.append(protein_source)
        
        # 2. Adicionar carboidratos
        remaining_carbs = target.carbs - sum(f.carbs for f in selected_foods)
        if remaining_carbs > 5:  # Se ainda precisamos de carboidratos significativos
            carb_foods = [f for f in suitable_foods if f.carbs_per_100g >= 20 and f not in selected_foods]
            carb_source = self._select_food_by_priority(carb_foods, remaining_carbs, "carbs")
            if carb_source:
                selected_foods.append(carb_source)
        
        # 3. Adicionar gorduras
        remaining_fat = target.fat - sum(f.fat for f in selected_foods)
        if remaining_fat > 2:  # Se ainda precisamos de gorduras
            fat_foods = [f for f in suitable_foods if f.fat_per_100g >= 10 and f not in selected_foods]
            fat_source = self._select_food_by_priority(fat_foods, remaining_fat, "fat")
            if fat_source:
                selected_foods.append(fat_source)
        
        # 4. Completar com alimentos complementares
        remaining_calories = target.calories - sum(f.calories_per_100g for f in selected_foods)
        if remaining_calories > 50:
            complementary_foods = [f for f in suitable_foods if f not in selected_foods]
            complement = self._select_food_by_priority(complementary_foods, remaining_calories, "calories")
            if complement:
                selected_foods.append(complement)
        
        # Calcular quantidades otimizadas
        food_items = self._optimize_quantities(selected_foods, target)
        
        # Calcular totais da refeição
        total_calories = sum(item.calories for item in food_items)
        total_protein = sum(item.protein for item in food_items)
        total_carbs = sum(item.carbs for item in food_items)
        total_fat = sum(item.fat for item in food_items)
        
        # Gerar instruções e dicas
        instructions = self._generate_meal_instructions(meal_type, food_items)
        tips = self._generate_meal_tips(meal_type, target, user_data)
        
        return Meal(
            meal_type=meal_type,
            name=self._generate_meal_name(meal_type, food_items),
            time_suggestion=self._get_meal_time_suggestion(meal_type),
            foods=food_items,
            total_calories=total_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat,
            preparation_time=max(food.preparation_time for food in selected_foods) if selected_foods else 15,
            instructions=instructions,
            tips=tips
        )
    
    def _filter_foods_for_meal(self, meal_type: MealType, foods: List[FoodCandidate]) -> List[FoodCandidate]:
        """Filtra alimentos apropriados para um tipo de refeição"""
        meal_categories = {
            MealType.CAFE_DA_MANHA: ["frutas", "cereais", "laticínios", "ovos", "pães"],
            MealType.LANCHE_MANHA: ["frutas", "oleaginosas", "laticínios", "barras"],
            MealType.ALMOCO: ["carnes", "peixes", "cereais", "vegetais", "leguminosas"],
            MealType.LANCHE_TARDE: ["frutas", "oleaginosas", "laticínios", "barras"],
            MealType.JANTAR: ["carnes", "peixes", "vegetais", "leguminosas", "cereais"],
            MealType.CEIA: ["laticínios", "oleaginosas", "proteínas"]
        }
        
        appropriate_categories = meal_categories.get(meal_type, [])
        
        return [
            food for food in foods 
            if food.category in appropriate_categories or "universal" in food.category
        ]
    
    def _select_food_by_priority(
        self, 
        foods: List[FoodCandidate], 
        target_amount: float, 
        nutrient: str
    ) -> Optional[FoodCandidate]:
        """Seleciona alimento baseado na prioridade e adequação nutricional"""
        if not foods:
            return None
        
        # Calcular score para cada alimento
        scored_foods = []
        for food in foods:
            nutrient_per_100g = getattr(food, f"{nutrient}_per_100g")
            
            # Score baseado na adequação nutricional
            adequacy_score = min(nutrient_per_100g / max(target_amount, 1), 2.0)
            
            # Score final combina adequação e preferência
            final_score = (adequacy_score * 0.7) + (food.preference_score * 0.3)
            
            scored_foods.append((food, final_score))
        
        # Ordenar por score e adicionar aleatoriedade para variedade
        scored_foods.sort(key=lambda x: x[1], reverse=True)
        
        # Selecionar entre os top 3 para adicionar variedade
        top_foods = scored_foods[:3]
        weights = [food[1] for food in top_foods]
        
        if weights:
            selected = random.choices(top_foods, weights=weights, k=1)[0]
            return selected[0]
        
        return None
    
    def _optimize_quantities(
        self, 
        selected_foods: List[FoodCandidate], 
        target: NutritionalTarget
    ) -> List[FoodItem]:
        """Otimiza as quantidades dos alimentos selecionados"""
        if not selected_foods:
            return []
        
        food_items = []
        
        # Algoritmo simples de otimização
        # Para cada alimento, calcular quantidade baseada na contribuição proporcional
        total_priority_score = sum(food.preference_score for food in selected_foods)
        
        for food in selected_foods:
            # Calcular contribuição proporcional baseada no score
            proportion = food.preference_score / total_priority_score if total_priority_score > 0 else 1.0 / len(selected_foods)
            
            # Calcular quantidade inicial baseada nas calorias alvo
            target_calories_for_food = target.calories * proportion
            quantity_grams = (target_calories_for_food / food.calories_per_100g) * 100
            
            # Ajustar para quantidades práticas
            quantity_grams = self._round_to_practical_quantity(quantity_grams, food.category)
            
            # Calcular valores nutricionais finais
            multiplier = quantity_grams / 100
            
            food_item = FoodItem(
                food_id=food.food_id,
                name=food.name,
                quantity=quantity_grams,
                unit="gramas",
                calories=food.calories_per_100g * multiplier,
                protein=food.protein_per_100g * multiplier,
                carbs=food.carbs_per_100g * multiplier,
                fat=food.fat_per_100g * multiplier
            )
            
            food_items.append(food_item)
        
        return food_items
    
    def _round_to_practical_quantity(self, quantity: float, category: str) -> float:
        """Arredonda para quantidades práticas baseadas na categoria"""
        practical_rounds = {
            "frutas": 50,      # Múltiplos de 50g
            "vegetais": 50,    # Múltiplos de 50g
            "carnes": 25,      # Múltiplos de 25g
            "cereais": 25,     # Múltiplos de 25g
            "laticínios": 50,  # Múltiplos de 50g
            "oleaginosas": 10, # Múltiplos de 10g
            "default": 25      # Padrão
        }
        
        round_to = practical_rounds.get(category, practical_rounds["default"])
        return round(quantity / round_to) * round_to
    
    def _calculate_totals(self, meals: List[Meal]) -> Tuple[float, float, float, float]:
        """Calcula totais nutricionais do plano"""
        total_calories = sum(meal.total_calories for meal in meals)
        total_protein = sum(meal.total_protein for meal in meals)
        total_carbs = sum(meal.total_carbs for meal in meals)
        total_fat = sum(meal.total_fat for meal in meals)
        
        return total_calories, total_protein, total_carbs, total_fat
    
    def _needs_adjustment(self, actual_calories: float, target_calories: float) -> bool:
        """Verifica se o plano precisa de ajuste"""
        tolerance = self.diet_config["tolerance"]["calories"]
        difference = abs(actual_calories - target_calories) / target_calories
        return difference > tolerance
    
    async def _adjust_plan(
        self, 
        meals: List[Meal], 
        config: AlgorithmConfig,
        available_foods: List[FoodCandidate]
    ) -> List[Meal]:
        """Ajusta o plano para atingir os alvos nutricionais"""
        # Implementação simplificada - ajustar quantidades proporcionalmente
        current_calories = sum(meal.total_calories for meal in meals)
        target_calories = config.target_calories
        
        adjustment_factor = target_calories / current_calories if current_calories > 0 else 1.0
        
        adjusted_meals = []
        for meal in meals:
            adjusted_foods = []
            for food in meal.foods:
                # Ajustar quantidade
                new_quantity = food.quantity * adjustment_factor
                new_quantity = self._round_to_practical_quantity(new_quantity, "default")
                
                # Recalcular valores nutricionais
                multiplier = new_quantity / 100
                adjusted_food = FoodItem(
                    food_id=food.food_id,
                    name=food.name,
                    quantity=new_quantity,
                    unit=food.unit,
                    calories=food.calories * adjustment_factor,
                    protein=food.protein * adjustment_factor,
                    carbs=food.carbs * adjustment_factor,
                    fat=food.fat * adjustment_factor
                )
                adjusted_foods.append(adjusted_food)
            
            # Recalcular totais da refeição
            total_calories = sum(item.calories for item in adjusted_foods)
            total_protein = sum(item.protein for item in adjusted_foods)
            total_carbs = sum(item.carbs for item in adjusted_foods)
            total_fat = sum(item.fat for item in adjusted_foods)
            
            adjusted_meal = Meal(
                meal_type=meal.meal_type,
                name=meal.name,
                time_suggestion=meal.time_suggestion,
                foods=adjusted_foods,
                total_calories=total_calories,
                total_protein=total_protein,
                total_carbs=total_carbs,
                total_fat=total_fat,
                preparation_time=meal.preparation_time,
                instructions=meal.instructions,
                tips=meal.tips
            )
            adjusted_meals.append(adjusted_meal)
        
        return adjusted_meals
    
    # Métodos auxiliares
    
    async def _get_existing_plan(self, user_id: str, target_date: date) -> Optional[DietPlan]:
        """Busca plano existente no Firestore"""
        try:
            doc_ref = self.firebase_service.db.collection("diet_plans").document(f"{user_id}_{target_date}")
            doc = await doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return DietPlan(**data)
            
            return None
        except Exception as e:
            logger.error("Erro ao buscar plano existente", error=str(e))
            return None
    
    def _should_regenerate_plan(self, existing_plan: DietPlan, config: AlgorithmConfig) -> bool:
        """Verifica se deve regenerar um plano existente"""
        # Regenerar se as metas calóricas mudaram significativamente
        calorie_difference = abs(existing_plan.target_calories - config.target_calories)
        if calorie_difference > 100:  # Diferença maior que 100 calorias
            return True
        
        # Regenerar se o objetivo mudou
        if existing_plan.goal != config.goal:
            return True
        
        # Regenerar se o plano é muito antigo (mais de 7 dias)
        if existing_plan.created_at < datetime.utcnow() - timedelta(days=7):
            return True
        
        return False
    
    async def _get_user_data(self, user_id: str) -> dict:
        """Obtém dados do usuário"""
        try:
            doc_ref = self.firebase_service.db.collection("users").document(user_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                logger.warning("Dados do usuário não encontrados", user_id=user_id)
                return {}
        except Exception as e:
            logger.error("Erro ao obter dados do usuário", user_id=user_id, error=str(e))
            return {}
    
    def _calculate_water_intake(self, config: AlgorithmConfig) -> int:
        """Calcula ingestão de água recomendada em ml"""
        # Fórmula básica: 35ml por kg de peso corporal
        # Como não temos peso aqui, usar base de 2000ml e ajustar por atividade
        base_water = 2000
        
        # Ajustar baseado no objetivo
        if config.goal == GoalType.PERDER_PESO:
            return int(base_water * 1.2)  # +20% para perda de peso
        elif config.goal == GoalType.GANHAR_MASSA:
            return int(base_water * 1.1)  # +10% para ganho de massa
        else:
            return base_water
    
    def _generate_diet_notes(self, config: AlgorithmConfig, preferences: DietPreferences) -> str:
        """Gera notas personalizadas para o plano de dieta"""
        notes = []
        
        if config.goal == GoalType.PERDER_PESO:
            notes.append("Foque em manter o déficit calórico e beber bastante água.")
        elif config.goal == GoalType.GANHAR_MASSA:
            notes.append("Distribua as proteínas ao longo do dia para otimizar a síntese proteica.")
        
        if preferences.style == "varied":
            notes.append("Plano variado para manter a motivação e aderência.")
        else:
            notes.append("Plano consistente para facilitar a preparação e controle.")
        
        return " ".join(notes)
    
    def _generate_meal_name(self, meal_type: MealType, food_items: List[FoodItem]) -> str:
        """Gera nome atrativo para a refeição"""
        if not food_items:
            return meal_type.value.replace("_", " ").title()
        
        main_food = food_items[0].name
        
        meal_names = {
            MealType.CAFE_DA_MANHA: f"Café da Manhã com {main_food}",
            MealType.LANCHE_MANHA: f"Lanche da Manhã - {main_food}",
            MealType.ALMOCO: f"Almoço - {main_food}",
            MealType.LANCHE_TARDE: f"Lanche da Tarde - {main_food}",
            MealType.JANTAR: f"Jantar - {main_food}",
            MealType.CEIA: f"Ceia - {main_food}"
        }
        
        return meal_names.get(meal_type, f"{meal_type.value} - {main_food}")
    
    def _get_meal_time_suggestion(self, meal_type: MealType) -> Optional[str]:
        """Sugere horário para a refeição"""
        time_suggestions = {
            MealType.CAFE_DA_MANHA: "07:00",
            MealType.LANCHE_MANHA: "10:00",
            MealType.ALMOCO: "12:30",
            MealType.LANCHE_TARDE: "15:30",
            MealType.JANTAR: "19:00",
            MealType.CEIA: "21:30"
        }
        
        return time_suggestions.get(meal_type)
    
    def _generate_meal_instructions(self, meal_type: MealType, food_items: List[FoodItem]) -> str:
        """Gera instruções de preparo para a refeição"""
        if not food_items:
            return "Siga as instruções de preparo de cada alimento."
        
        # Instruções básicas baseadas no tipo de refeição
        instructions = {
            MealType.CAFE_DA_MANHA: "Prepare os alimentos frescos. Consuma logo após o preparo.",
            MealType.LANCHE_MANHA: "Pode ser preparado com antecedência. Mantenha refrigerado se necessário.",
            MealType.ALMOCO: "Cozinhe os alimentos adequadamente. Tempere a gosto.",
            MealType.LANCHE_TARDE: "Prepare na hora do consumo para manter a qualidade.",
            MealType.JANTAR: "Prefira preparações mais leves. Evite frituras.",
            MealType.CEIA: "Opte por alimentos de fácil digestão."
        }
        
        return instructions.get(meal_type, "Siga as instruções de preparo adequadas.")
    
    def _generate_meal_tips(self, meal_type: MealType, target: NutritionalTarget, user_data: dict) -> List[str]:
        """Gera dicas personalizadas para a refeição"""
        tips = []
        
        # Dicas baseadas no tipo de refeição
        meal_tips = {
            MealType.CAFE_DA_MANHA: [
                "Inclua proteína para manter a saciedade",
                "Hidrate-se bem ao acordar"
            ],
            MealType.LANCHE_MANHA: [
                "Combine proteína com carboidrato",
                "Mantenha porções moderadas"
            ],
            MealType.ALMOCO: [
                "Mastigue bem os alimentos",
                "Inclua vegetais para fibras"
            ],
            MealType.LANCHE_TARDE: [
                "Evite açúcares simples em excesso",
                "Prefira alimentos naturais"
            ],
            MealType.JANTAR: [
                "Evite refeições muito pesadas",
                "Jante pelo menos 2h antes de dormir"
            ],
            MealType.CEIA: [
                "Opte por proteínas de digestão lenta",
                "Mantenha porções pequenas"
            ]
        }
        
        tips.extend(meal_tips.get(meal_type, []))
        
        return tips[:2]  # Máximo 2 dicas por refeição
    
    async def _save_diet_plan(self, diet_plan: DietPlan):
        """Salva o plano de dieta no Firestore"""
        try:
            doc_id = f"{diet_plan.user_id}_{diet_plan.date}"
            doc_ref = self.firebase_service.db.collection("diet_plans").document(doc_id)
            
            # Converter para dict
            plan_data = diet_plan.dict()
            plan_data["created_at"] = datetime.utcnow()
            plan_data["updated_at"] = datetime.utcnow()
            
            await doc_ref.set(plan_data)
            
            logger.info("Plano de dieta salvo", user_id=diet_plan.user_id, date=diet_plan.date)
            
        except Exception as e:
            logger.error("Erro ao salvar plano de dieta", error=str(e))
            raise


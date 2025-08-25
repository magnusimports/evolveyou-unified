"""
Serviço de cálculo calórico avançado
Implementa o Algoritmo de Gasto Calórico Aprimorado da EvolveYou
"""

import math
from datetime import datetime, date
from typing import Dict, Any, Tuple
import structlog

from config.settings import get_settings
from models.user import (
    HealthAssessment, LifestyleAssessment, FitnessGoals, 
    CalorieCalculation, Gender, ActivityLevel, 
    TrainingExperience, BodyComposition
)

logger = structlog.get_logger()
settings = get_settings()

class CalorieService:
    """Serviço para cálculos calóricos avançados"""
    
    def __init__(self):
        self.body_composition_factors = settings.body_composition_factors
        self.pharma_factors = settings.pharma_factors
        self.training_experience_factors = settings.training_experience_factors
        self.activity_factors = settings.activity_factors
    
    def calculate_age(self, date_of_birth: date) -> int:
        """Calcular idade em anos"""
        today = date.today()
        return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    
    def calculate_bmr_mifflin_st_jeor(
        self, 
        weight: float, 
        height: float, 
        age: int, 
        gender: Gender
    ) -> float:
        """
        Calcular Taxa Metabólica Basal usando fórmula Mifflin-St Jeor
        
        Homens: BMR = 10 × peso(kg) + 6.25 × altura(cm) - 5 × idade(anos) + 5
        Mulheres: BMR = 10 × peso(kg) + 6.25 × altura(cm) - 5 × idade(anos) - 161
        """
        try:
            base_bmr = 10 * weight + 6.25 * height - 5 * age
            
            if gender == Gender.MALE:
                bmr = base_bmr + 5
            elif gender == Gender.FEMALE:
                bmr = base_bmr - 161
            else:
                # Para outros gêneros, usar média
                bmr = base_bmr - 78  # Média entre +5 e -161
            
            logger.info(
                "BMR calculado",
                weight=weight,
                height=height,
                age=age,
                gender=gender,
                bmr=bmr
            )
            
            return round(bmr, 2)
            
        except Exception as e:
            logger.error("Erro no cálculo BMR", error=str(e))
            raise
    
    def calculate_bmr_harris_benedict(
        self, 
        weight: float, 
        height: float, 
        age: int, 
        gender: Gender
    ) -> float:
        """
        Calcular BMR usando fórmula Harris-Benedict (alternativa)
        
        Homens: BMR = 88.362 + (13.397 × peso) + (4.799 × altura) - (5.677 × idade)
        Mulheres: BMR = 447.593 + (9.247 × peso) + (3.098 × altura) - (4.330 × idade)
        """
        try:
            if gender == Gender.MALE:
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            elif gender == Gender.FEMALE:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            else:
                # Média entre homens e mulheres
                bmr_male = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
                bmr_female = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
                bmr = (bmr_male + bmr_female) / 2
            
            return round(bmr, 2)
            
        except Exception as e:
            logger.error("Erro no cálculo BMR Harris-Benedict", error=str(e))
            raise
    
    def determine_body_composition_category(
        self, 
        body_fat_percentage: float, 
        gender: Gender
    ) -> str:
        """
        Determinar categoria de composição corporal baseada no % de gordura
        
        Homens:
        - Muito baixo: <10%
        - Baixo: 10-15%
        - Normal: 15-20%
        - Alto: 20-25%
        - Muito alto: >25%
        
        Mulheres:
        - Muito baixo: <16%
        - Baixo: 16-20%
        - Normal: 20-25%
        - Alto: 25-30%
        - Muito alto: >30%
        """
        try:
            if gender == Gender.MALE:
                if body_fat_percentage < 10:
                    return "muito_baixo"
                elif body_fat_percentage < 15:
                    return "baixo"
                elif body_fat_percentage < 20:
                    return "normal"
                elif body_fat_percentage < 25:
                    return "alto"
                else:
                    return "muito_alto"
            
            elif gender == Gender.FEMALE:
                if body_fat_percentage < 16:
                    return "muito_baixo"
                elif body_fat_percentage < 20:
                    return "baixo"
                elif body_fat_percentage < 25:
                    return "normal"
                elif body_fat_percentage < 30:
                    return "alto"
                else:
                    return "muito_alto"
            
            else:
                # Para outros gêneros, usar média dos critérios
                if body_fat_percentage < 13:  # Média de 10 e 16
                    return "muito_baixo"
                elif body_fat_percentage < 17.5:  # Média de 15 e 20
                    return "baixo"
                elif body_fat_percentage < 22.5:  # Média de 20 e 25
                    return "normal"
                elif body_fat_percentage < 27.5:  # Média de 25 e 30
                    return "alto"
                else:
                    return "muito_alto"
                    
        except Exception as e:
            logger.error("Erro ao determinar composição corporal", error=str(e))
            return "normal"  # Padrão seguro
    
    def calculate_body_composition_factor(
        self, 
        health_assessment: HealthAssessment, 
        gender: Gender
    ) -> Tuple[float, str]:
        """Calcular fator de composição corporal"""
        try:
            if health_assessment.body_fat_percentage:
                # Usar % de gordura fornecido
                category = self.determine_body_composition_category(
                    health_assessment.body_fat_percentage, 
                    gender
                )
            else:
                # Estimar baseado em outras medidas
                category = self.estimate_body_composition_from_measurements(
                    health_assessment, 
                    gender
                )
            
            factor = self.body_composition_factors.get(category, 1.0)
            
            logger.info(
                "Fator de composição corporal calculado",
                category=category,
                factor=factor
            )
            
            return factor, category
            
        except Exception as e:
            logger.error("Erro no cálculo do fator de composição corporal", error=str(e))
            return 1.0, "normal"
    
    def estimate_body_composition_from_measurements(
        self, 
        health_assessment: HealthAssessment, 
        gender: Gender
    ) -> str:
        """Estimar composição corporal a partir de medidas corporais"""
        try:
            # Calcular IMC
            height_m = health_assessment.height / 100
            bmi = health_assessment.weight / (height_m ** 2)
            
            # Usar relação cintura-quadril se disponível
            waist_hip_ratio = None
            if (health_assessment.waist_circumference and 
                health_assessment.hip_circumference):
                waist_hip_ratio = (health_assessment.waist_circumference / 
                                 health_assessment.hip_circumference)
            
            # Estimativa baseada em IMC e relação cintura-quadril
            if gender == Gender.MALE:
                if bmi < 20:
                    return "baixo"
                elif bmi < 25:
                    if waist_hip_ratio and waist_hip_ratio < 0.85:
                        return "baixo"
                    else:
                        return "normal"
                elif bmi < 30:
                    return "alto"
                else:
                    return "muito_alto"
            
            elif gender == Gender.FEMALE:
                if bmi < 19:
                    return "baixo"
                elif bmi < 24:
                    if waist_hip_ratio and waist_hip_ratio < 0.80:
                        return "baixo"
                    else:
                        return "normal"
                elif bmi < 29:
                    return "alto"
                else:
                    return "muito_alto"
            
            else:
                # Média para outros gêneros
                if bmi < 19.5:
                    return "baixo"
                elif bmi < 24.5:
                    return "normal"
                elif bmi < 29.5:
                    return "alto"
                else:
                    return "muito_alto"
                    
        except Exception as e:
            logger.error("Erro na estimativa de composição corporal", error=str(e))
            return "normal"
    
    def calculate_pharma_factor(self, medical_history) -> Tuple[float, list]:
        """Calcular fator de suplementação/medicamentos"""
        try:
            supplements = getattr(medical_history, 'supplements', [])
            
            if not supplements:
                return 1.0, []
            
            # Mapear suplementos para fatores
            supplement_mapping = {
                "termogênico": "termogenico",
                "termogenico": "termogenico",
                "creatina": "creatina",
                "whey protein": "whey_protein",
                "whey": "whey_protein",
                "proteína": "whey_protein",
                "multivitamínico": "multivitaminico",
                "multivitaminico": "multivitaminico",
                "vitaminas": "multivitaminico",
                "ômega 3": "omega3",
                "omega3": "omega3",
                "omega 3": "omega3",
                "cafeína": "cafeina",
                "cafeina": "cafeina",
                "pré-treino": "pre_treino",
                "pre treino": "pre_treino",
                "pre_treino": "pre_treino"
            }
            
            total_factor = 1.0
            applied_supplements = []
            
            for supplement in supplements:
                supplement_lower = supplement.lower().strip()
                
                for key, factor_key in supplement_mapping.items():
                    if key in supplement_lower:
                        factor = self.pharma_factors.get(factor_key, 1.0)
                        total_factor *= factor
                        applied_supplements.append(factor_key)
                        break
            
            # Limitar fator máximo para evitar valores extremos
            total_factor = min(total_factor, 1.15)  # Máximo 15% de aumento
            
            logger.info(
                "Fator de suplementação calculado",
                supplements=supplements,
                applied_supplements=applied_supplements,
                factor=total_factor
            )
            
            return total_factor, applied_supplements
            
        except Exception as e:
            logger.error("Erro no cálculo do fator de suplementação", error=str(e))
            return 1.0, []
    
    def calculate_training_experience_factor(self, fitness_goals: FitnessGoals) -> float:
        """Calcular fator de experiência de treinamento"""
        try:
            experience = fitness_goals.training_experience
            factor = self.training_experience_factors.get(experience, 1.0)
            
            logger.info(
                "Fator de experiência calculado",
                experience=experience,
                factor=factor
            )
            
            return factor
            
        except Exception as e:
            logger.error("Erro no cálculo do fator de experiência", error=str(e))
            return 1.0
    
    def calculate_activity_factor(self, lifestyle_assessment: LifestyleAssessment) -> float:
        """Calcular fator de atividade combinado (trabalho + lazer)"""
        try:
            work_factor = self.activity_factors.get(lifestyle_assessment.work_activity_level, 1.2)
            leisure_factor = self.activity_factors.get(lifestyle_assessment.leisure_activity_level, 1.2)
            
            # Combinar fatores de trabalho e lazer
            # Fórmula: (work_factor * 0.6) + (leisure_factor * 0.4)
            # Trabalho tem peso maior pois ocupa mais tempo do dia
            combined_factor = (work_factor * 0.6) + (leisure_factor * 0.4)
            
            # Ajustar baseado nos dias de treino disponíveis
            training_days = lifestyle_assessment.available_days_per_week
            if training_days >= 5:
                combined_factor *= 1.05  # Boost para quem treina muito
            elif training_days <= 2:
                combined_factor *= 0.95  # Redução para quem treina pouco
            
            logger.info(
                "Fator de atividade calculado",
                work_level=lifestyle_assessment.work_activity_level,
                leisure_level=lifestyle_assessment.leisure_activity_level,
                training_days=training_days,
                work_factor=work_factor,
                leisure_factor=leisure_factor,
                combined_factor=combined_factor
            )
            
            return round(combined_factor, 3)
            
        except Exception as e:
            logger.error("Erro no cálculo do fator de atividade", error=str(e))
            return 1.375  # Padrão: levemente ativo
    
    def calculate_macronutrients(
        self, 
        calories: float, 
        fitness_goals: FitnessGoals,
        body_weight: float
    ) -> Tuple[float, float, float]:
        """
        Calcular distribuição de macronutrientes
        
        Returns:
            Tuple[protein_grams, carbs_grams, fat_grams]
        """
        try:
            primary_goal = fitness_goals.primary_goal
            
            # Definir distribuição baseada no objetivo
            if primary_goal == "ganhar_massa":
                # Bulking: mais carboidratos
                protein_ratio = 0.25  # 25%
                carbs_ratio = 0.45    # 45%
                fat_ratio = 0.30      # 30%
                
            elif primary_goal == "perder_peso":
                # Cutting: mais proteína, menos carboidratos
                protein_ratio = 0.35  # 35%
                carbs_ratio = 0.30    # 30%
                fat_ratio = 0.35      # 35%
                
            elif primary_goal == "aumentar_forca":
                # Força: balanceado com foco em proteína
                protein_ratio = 0.30  # 30%
                carbs_ratio = 0.40    # 40%
                fat_ratio = 0.30      # 30%
                
            else:
                # Manutenção/saúde: distribuição balanceada
                protein_ratio = 0.25  # 25%
                carbs_ratio = 0.45    # 45%
                fat_ratio = 0.30      # 30%
            
            # Calcular gramas
            protein_calories = calories * protein_ratio
            carbs_calories = calories * carbs_ratio
            fat_calories = calories * fat_ratio
            
            # Converter para gramas (4 kcal/g proteína e carbs, 9 kcal/g gordura)
            protein_grams = protein_calories / 4
            carbs_grams = carbs_calories / 4
            fat_grams = fat_calories / 9
            
            # Validar proteína mínima (1.6-2.2g/kg peso corporal)
            min_protein = body_weight * 1.6
            max_protein = body_weight * 2.5
            
            if protein_grams < min_protein:
                protein_grams = min_protein
                # Reajustar outros macros
                remaining_calories = calories - (protein_grams * 4)
                carbs_grams = (remaining_calories * 0.6) / 4
                fat_grams = (remaining_calories * 0.4) / 9
            
            elif protein_grams > max_protein:
                protein_grams = max_protein
                # Reajustar outros macros
                remaining_calories = calories - (protein_grams * 4)
                carbs_grams = (remaining_calories * 0.6) / 4
                fat_grams = (remaining_calories * 0.4) / 9
            
            logger.info(
                "Macronutrientes calculados",
                goal=primary_goal,
                calories=calories,
                protein_grams=round(protein_grams, 1),
                carbs_grams=round(carbs_grams, 1),
                fat_grams=round(fat_grams, 1)
            )
            
            return (
                round(protein_grams, 1),
                round(carbs_grams, 1),
                round(fat_grams, 1)
            )
            
        except Exception as e:
            logger.error("Erro no cálculo de macronutrientes", error=str(e))
            # Retornar valores padrão
            protein_grams = body_weight * 2.0
            remaining_calories = calories - (protein_grams * 4)
            carbs_grams = (remaining_calories * 0.5) / 4
            fat_grams = (remaining_calories * 0.5) / 9
            
            return (
                round(protein_grams, 1),
                round(carbs_grams, 1),
                round(fat_grams, 1)
            )
    
    async def calculate_calories(
        self,
        health_assessment: HealthAssessment,
        lifestyle_assessment: LifestyleAssessment,
        fitness_goals: FitnessGoals,
        gender: Gender,
        date_of_birth: date
    ) -> CalorieCalculation:
        """
        Calcular calorias usando o Algoritmo de Gasto Calórico Aprimorado
        
        Etapas:
        1. Calcular BMR base (Mifflin-St Jeor)
        2. Aplicar fatores de ajuste
        3. Calcular TDEE (Total Daily Energy Expenditure)
        4. Calcular metas calóricas por objetivo
        5. Calcular macronutrientes
        """
        try:
            logger.info("Iniciando cálculo calórico avançado")
            
            # 1. Calcular idade
            age = self.calculate_age(date_of_birth)
            
            # 2. Calcular BMR base
            if settings.bmr_formula == "harris_benedict":
                bmr_base = self.calculate_bmr_harris_benedict(
                    health_assessment.weight,
                    health_assessment.height,
                    age,
                    gender
                )
            else:
                bmr_base = self.calculate_bmr_mifflin_st_jeor(
                    health_assessment.weight,
                    health_assessment.height,
                    age,
                    gender
                )
            
            # 3. Calcular fatores de ajuste
            body_comp_factor, body_comp_category = self.calculate_body_composition_factor(
                health_assessment, gender
            )
            
            pharma_factor, applied_supplements = self.calculate_pharma_factor(
                getattr(fitness_goals, 'medical_history', None) or 
                type('obj', (object,), {'supplements': []})()
            )
            
            training_factor = self.calculate_training_experience_factor(fitness_goals)
            
            activity_factor = self.calculate_activity_factor(lifestyle_assessment)
            
            # 4. Calcular BMR ajustado
            bmr_adjusted = bmr_base * body_comp_factor * pharma_factor * training_factor
            
            # 5. Calcular TDEE (Gasto Calórico Diário Total)
            tdee = bmr_adjusted * activity_factor
            
            # 6. Calcular metas calóricas por objetivo
            maintenance_calories = tdee
            
            # Cutting: déficit de 15-25% dependendo do objetivo
            if fitness_goals.primary_goal == "perder_peso":
                cutting_deficit = 0.20  # 20% de déficit
            else:
                cutting_deficit = 0.15  # 15% de déficit conservador
            
            cutting_calories = maintenance_calories * (1 - cutting_deficit)
            
            # Bulking: superávit de 10-20%
            if fitness_goals.primary_goal == "ganhar_massa":
                bulking_surplus = 0.15  # 15% de superávit
            else:
                bulking_surplus = 0.10  # 10% de superávit conservador
            
            bulking_calories = maintenance_calories * (1 + bulking_surplus)
            
            # 7. Calcular macronutrientes para manutenção
            protein_grams, carbs_grams, fat_grams = self.calculate_macronutrients(
                maintenance_calories,
                fitness_goals,
                health_assessment.weight
            )
            
            # 8. Criar resultado
            calorie_calculation = CalorieCalculation(
                bmr=round(bmr_adjusted, 1),
                tdee=round(tdee, 1),
                body_composition_factor=body_comp_factor,
                pharma_factor=pharma_factor,
                training_experience_factor=training_factor,
                activity_factor=activity_factor,
                maintenance_calories=round(maintenance_calories, 1),
                cutting_calories=round(cutting_calories, 1),
                bulking_calories=round(bulking_calories, 1),
                protein_grams=protein_grams,
                carbs_grams=carbs_grams,
                fat_grams=fat_grams,
                calculated_at=datetime.utcnow(),
                formula_used=settings.bmr_formula
            )
            
            logger.info(
                "Cálculo calórico concluído",
                bmr_base=bmr_base,
                bmr_adjusted=bmr_adjusted,
                tdee=tdee,
                maintenance_calories=maintenance_calories,
                body_comp_factor=body_comp_factor,
                pharma_factor=pharma_factor,
                training_factor=training_factor,
                activity_factor=activity_factor
            )
            
            return calorie_calculation
            
        except Exception as e:
            logger.error("Erro no cálculo calórico", error=str(e))
            raise


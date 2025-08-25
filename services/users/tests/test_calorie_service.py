"""
Testes para o serviço de cálculo calórico
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch

from src.services.calorie_service import CalorieService
from src.models.user import (
    HealthAssessment, LifestyleAssessment, FitnessGoals, 
    Gender, ActivityLevel, TrainingExperience, CalorieCalculation
)

@pytest.fixture
def calorie_service():
    """Instância do serviço de cálculo calórico"""
    return CalorieService()

@pytest.fixture
def sample_health_assessment():
    """Avaliação de saúde de exemplo"""
    return HealthAssessment(
        height=175.0,
        weight=80.0,
        body_fat_percentage=15.0,
        waist_circumference=85.0,
        hip_circumference=95.0,
        resting_heart_rate=65,
        max_heart_rate=185,
        systolic_pressure=120,
        diastolic_pressure=80
    )

@pytest.fixture
def sample_lifestyle_assessment():
    """Avaliação de estilo de vida de exemplo"""
    return LifestyleAssessment(
        work_activity_level=ActivityLevel.SEDENTARY,
        leisure_activity_level=ActivityLevel.MODERATELY_ACTIVE,
        available_days_per_week=4,
        preferred_workout_duration=60,
        sleep_hours=7.5,
        stress_level=3,
        water_intake=2.5
    )

@pytest.fixture
def sample_fitness_goals():
    """Objetivos fitness de exemplo"""
    return FitnessGoals(
        primary_goal="ganhar_massa",
        target_weight=85.0,
        timeline_weeks=16,
        training_experience=TrainingExperience.INTERMEDIATE,
        available_days_per_week=4,
        preferred_workout_types=["musculacao", "cardio"]
    )

class TestCalorieService:
    """Testes para CalorieService"""
    
    def test_calculate_age(self, calorie_service):
        """Testar cálculo de idade"""
        # Pessoa nascida em 1990
        birth_date = date(1990, 5, 15)
        age = calorie_service.calculate_age(birth_date)
        
        # Verificar que a idade está correta (considerando 2025)
        assert age >= 34 and age <= 35
        
        # Pessoa nascida em 2000
        birth_date = date(2000, 1, 1)
        age = calorie_service.calculate_age(birth_date)
        assert age >= 24 and age <= 25
    
    def test_calculate_bmr_mifflin_st_jeor_male(self, calorie_service):
        """Testar cálculo BMR para homem"""
        weight = 80.0
        height = 175.0
        age = 30
        gender = Gender.MALE
        
        bmr = calorie_service.calculate_bmr_mifflin_st_jeor(weight, height, age, gender)
        
        # Fórmula: 10 × 80 + 6.25 × 175 - 5 × 30 + 5 = 1738.75
        expected_bmr = 10 * weight + 6.25 * height - 5 * age + 5
        assert bmr == round(expected_bmr, 2)
        assert bmr > 1700  # Valor razoável para homem adulto
    
    def test_calculate_bmr_mifflin_st_jeor_female(self, calorie_service):
        """Testar cálculo BMR para mulher"""
        weight = 65.0
        height = 165.0
        age = 28
        gender = Gender.FEMALE
        
        bmr = calorie_service.calculate_bmr_mifflin_st_jeor(weight, height, age, gender)
        
        # Fórmula: 10 × 65 + 6.25 × 165 - 5 × 28 - 161 = 1370.25
        expected_bmr = 10 * weight + 6.25 * height - 5 * age - 161
        assert bmr == round(expected_bmr, 2)
        assert bmr > 1300  # Valor razoável para mulher adulta
    
    def test_calculate_bmr_harris_benedict_male(self, calorie_service):
        """Testar cálculo BMR Harris-Benedict para homem"""
        weight = 80.0
        height = 175.0
        age = 30
        gender = Gender.MALE
        
        bmr = calorie_service.calculate_bmr_harris_benedict(weight, height, age, gender)
        
        # Fórmula: 88.362 + (13.397 × 80) + (4.799 × 175) - (5.677 × 30)
        expected_bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        assert bmr == round(expected_bmr, 2)
        assert bmr > 1700
    
    def test_determine_body_composition_category_male(self, calorie_service):
        """Testar determinação de categoria de composição corporal - homem"""
        gender = Gender.MALE
        
        # Muito baixo
        assert calorie_service.determine_body_composition_category(8.0, gender) == "muito_baixo"
        
        # Baixo
        assert calorie_service.determine_body_composition_category(12.0, gender) == "baixo"
        
        # Normal
        assert calorie_service.determine_body_composition_category(17.0, gender) == "normal"
        
        # Alto
        assert calorie_service.determine_body_composition_category(22.0, gender) == "alto"
        
        # Muito alto
        assert calorie_service.determine_body_composition_category(28.0, gender) == "muito_alto"
    
    def test_determine_body_composition_category_female(self, calorie_service):
        """Testar determinação de categoria de composição corporal - mulher"""
        gender = Gender.FEMALE
        
        # Muito baixo
        assert calorie_service.determine_body_composition_category(14.0, gender) == "muito_baixo"
        
        # Baixo
        assert calorie_service.determine_body_composition_category(18.0, gender) == "baixo"
        
        # Normal
        assert calorie_service.determine_body_composition_category(23.0, gender) == "normal"
        
        # Alto
        assert calorie_service.determine_body_composition_category(27.0, gender) == "alto"
        
        # Muito alto
        assert calorie_service.determine_body_composition_category(32.0, gender) == "muito_alto"
    
    def test_calculate_body_composition_factor(self, calorie_service, sample_health_assessment):
        """Testar cálculo do fator de composição corporal"""
        gender = Gender.MALE
        
        factor, category = calorie_service.calculate_body_composition_factor(
            sample_health_assessment, gender
        )
        
        # Com 15% de gordura corporal para homem, deve ser "normal"
        assert category == "normal"
        assert isinstance(factor, float)
        assert factor > 0.8 and factor < 1.2  # Fator razoável
    
    def test_estimate_body_composition_from_measurements(self, calorie_service, sample_health_assessment):
        """Testar estimativa de composição corporal a partir de medidas"""
        gender = Gender.MALE
        
        # Remover % de gordura para forçar estimativa
        health_no_bf = HealthAssessment(
            height=sample_health_assessment.height,
            weight=sample_health_assessment.weight,
            waist_circumference=sample_health_assessment.waist_circumference,
            hip_circumference=sample_health_assessment.hip_circumference
        )
        
        category = calorie_service.estimate_body_composition_from_measurements(
            health_no_bf, gender
        )
        
        assert category in ["muito_baixo", "baixo", "normal", "alto", "muito_alto"]
    
    def test_calculate_pharma_factor(self, calorie_service):
        """Testar cálculo do fator de suplementação"""
        # Mock do histórico médico com suplementos
        medical_history = type('obj', (object,), {
            'supplements': ["creatina", "whey protein", "multivitamínico"]
        })()
        
        factor, applied = calorie_service.calculate_pharma_factor(medical_history)
        
        assert isinstance(factor, float)
        assert factor >= 1.0  # Fator deve ser >= 1.0
        assert factor <= 1.15  # Limitado a 15% de aumento
        assert isinstance(applied, list)
        assert len(applied) > 0  # Deve ter aplicado alguns suplementos
    
    def test_calculate_pharma_factor_no_supplements(self, calorie_service):
        """Testar fator de suplementação sem suplementos"""
        medical_history = type('obj', (object,), {'supplements': []})()
        
        factor, applied = calorie_service.calculate_pharma_factor(medical_history)
        
        assert factor == 1.0
        assert applied == []
    
    def test_calculate_training_experience_factor(self, calorie_service, sample_fitness_goals):
        """Testar cálculo do fator de experiência"""
        factor = calorie_service.calculate_training_experience_factor(sample_fitness_goals)
        
        assert isinstance(factor, float)
        assert factor > 0.8 and factor < 1.2  # Fator razoável
    
    def test_calculate_activity_factor(self, calorie_service, sample_lifestyle_assessment):
        """Testar cálculo do fator de atividade"""
        factor = calorie_service.calculate_activity_factor(sample_lifestyle_assessment)
        
        assert isinstance(factor, float)
        assert factor > 1.0 and factor < 2.0  # Fator de atividade típico
        
        # Verificar que considera trabalho e lazer
        # Sedentário no trabalho + moderadamente ativo no lazer
        # Deve resultar em fator intermediário
        assert factor > 1.2 and factor < 1.6
    
    def test_calculate_macronutrients_bulking(self, calorie_service, sample_fitness_goals):
        """Testar cálculo de macronutrientes para ganho de massa"""
        calories = 2500.0
        body_weight = 80.0
        
        # Objetivo: ganhar massa
        sample_fitness_goals.primary_goal = "ganhar_massa"
        
        protein, carbs, fat = calorie_service.calculate_macronutrients(
            calories, sample_fitness_goals, body_weight
        )
        
        # Verificar que os valores são razoáveis
        assert protein > 0 and protein < 300  # Gramas de proteína
        assert carbs > 0 and carbs < 400     # Gramas de carboidratos
        assert fat > 0 and fat < 150         # Gramas de gordura
        
        # Verificar que proteína está na faixa adequada (1.6-2.5g/kg)
        assert protein >= body_weight * 1.6
        assert protein <= body_weight * 2.5
        
        # Verificar que soma das calorias está próxima do target
        total_calories = (protein * 4) + (carbs * 4) + (fat * 9)
        assert abs(total_calories - calories) < 50  # Margem de 50 kcal
    
    def test_calculate_macronutrients_cutting(self, calorie_service, sample_fitness_goals):
        """Testar cálculo de macronutrientes para perda de peso"""
        calories = 2000.0
        body_weight = 80.0
        
        # Objetivo: perder peso
        sample_fitness_goals.primary_goal = "perder_peso"
        
        protein, carbs, fat = calorie_service.calculate_macronutrients(
            calories, sample_fitness_goals, body_weight
        )
        
        # Para cutting, deve ter mais proteína proporcionalmente
        protein_ratio = (protein * 4) / calories
        assert protein_ratio > 0.3  # Mais de 30% das calorias de proteína
        
        # Verificar proteína mínima
        assert protein >= body_weight * 1.6
    
    @pytest.mark.asyncio
    async def test_calculate_calories_complete(
        self, 
        calorie_service, 
        sample_health_assessment, 
        sample_lifestyle_assessment, 
        sample_fitness_goals
    ):
        """Testar cálculo calórico completo"""
        gender = Gender.MALE
        date_of_birth = date(1990, 5, 15)
        
        # Executar cálculo
        result = await calorie_service.calculate_calories(
            sample_health_assessment,
            sample_lifestyle_assessment,
            sample_fitness_goals,
            gender,
            date_of_birth
        )
        
        # Verificar tipo do resultado
        assert isinstance(result, CalorieCalculation)
        
        # Verificar valores básicos
        assert result.bmr > 1000 and result.bmr < 3000
        assert result.tdee > result.bmr  # TDEE deve ser maior que BMR
        assert result.maintenance_calories == result.tdee
        
        # Verificar metas calóricas
        assert result.cutting_calories < result.maintenance_calories
        assert result.bulking_calories > result.maintenance_calories
        
        # Verificar macronutrientes
        assert result.protein_grams > 0
        assert result.carbs_grams > 0
        assert result.fat_grams > 0
        
        # Verificar fatores
        assert result.body_composition_factor > 0
        assert result.pharma_factor > 0
        assert result.training_experience_factor > 0
        assert result.activity_factor > 0
        
        # Verificar metadados
        assert result.calculated_at is not None
        assert result.formula_used is not None
    
    @pytest.mark.asyncio
    async def test_calculate_calories_different_goals(
        self, 
        calorie_service, 
        sample_health_assessment, 
        sample_lifestyle_assessment
    ):
        """Testar cálculo calórico com diferentes objetivos"""
        gender = Gender.FEMALE
        date_of_birth = date(1995, 3, 20)
        
        # Testar diferentes objetivos
        goals = ["perder_peso", "ganhar_massa", "aumentar_forca", "manter_peso"]
        
        results = []
        for goal in goals:
            fitness_goals = FitnessGoals(
                primary_goal=goal,
                target_weight=60.0,
                timeline_weeks=12,
                training_experience=TrainingExperience.BEGINNER,
                available_days_per_week=3,
                preferred_workout_types=["musculacao"]
            )
            
            result = await calorie_service.calculate_calories(
                sample_health_assessment,
                sample_lifestyle_assessment,
                fitness_goals,
                gender,
                date_of_birth
            )
            
            results.append((goal, result))
        
        # Verificar que todos os resultados são válidos
        for goal, result in results:
            assert isinstance(result, CalorieCalculation)
            assert result.bmr > 0
            assert result.tdee > 0
            assert result.maintenance_calories > 0
    
    def test_macronutrients_calories_consistency(self, calorie_service, sample_fitness_goals):
        """Testar consistência entre macronutrientes e calorias"""
        calories = 2200.0
        body_weight = 75.0
        
        protein, carbs, fat = calorie_service.calculate_macronutrients(
            calories, sample_fitness_goals, body_weight
        )
        
        # Calcular calorias dos macronutrientes
        calculated_calories = (protein * 4) + (carbs * 4) + (fat * 9)
        
        # Deve estar próximo das calorias target (margem de 5%)
        difference = abs(calculated_calories - calories)
        tolerance = calories * 0.05  # 5% de tolerância
        
        assert difference <= tolerance, f"Diferença de {difference} kcal é maior que a tolerância de {tolerance} kcal"
    
    @pytest.mark.asyncio
    async def test_calculate_calories_edge_cases(self, calorie_service):
        """Testar casos extremos no cálculo calórico"""
        # Pessoa muito jovem
        young_health = HealthAssessment(height=160.0, weight=50.0)
        lifestyle = LifestyleAssessment(
            work_activity_level=ActivityLevel.SEDENTARY,
            leisure_activity_level=ActivityLevel.SEDENTARY,
            available_days_per_week=1
        )
        goals = FitnessGoals(
            primary_goal="manter_peso",
            training_experience=TrainingExperience.BEGINNER,
            available_days_per_week=1
        )
        
        result = await calorie_service.calculate_calories(
            young_health, lifestyle, goals, Gender.FEMALE, date(2005, 1, 1)
        )
        
        assert isinstance(result, CalorieCalculation)
        assert result.bmr > 0
        assert result.tdee > 0
        
        # Pessoa muito ativa
        active_lifestyle = LifestyleAssessment(
            work_activity_level=ActivityLevel.VERY_ACTIVE,
            leisure_activity_level=ActivityLevel.VERY_ACTIVE,
            available_days_per_week=7
        )
        
        result_active = await calorie_service.calculate_calories(
            young_health, active_lifestyle, goals, Gender.MALE, date(1985, 1, 1)
        )
        
        # Pessoa ativa deve ter TDEE maior
        assert result_active.tdee > result.tdee


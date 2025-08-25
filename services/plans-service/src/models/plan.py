"""
Modelos de dados para planos de dieta e treino
"""

from datetime import datetime, date, time
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

class MealType(str, Enum):
    """Tipos de refeições"""
    CAFE_DA_MANHA = "cafe_da_manha"
    LANCHE_MANHA = "lanche_manha"
    ALMOCO = "almoco"
    LANCHE_TARDE = "lanche_tarde"
    JANTAR = "jantar"
    CEIA = "ceia"

class WorkoutType(str, Enum):
    """Tipos de treino"""
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    FUNCTIONAL = "functional"
    HIIT = "hiit"
    RECOVERY = "recovery"

class DifficultyLevel(str, Enum):
    """Níveis de dificuldade"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class GoalType(str, Enum):
    """Tipos de objetivos"""
    PERDER_PESO = "perder_peso"
    GANHAR_MASSA = "ganhar_massa"
    AUMENTAR_FORCA = "aumentar_forca"
    MELHORAR_RESISTENCIA = "melhorar_resistencia"
    MANTER_PESO = "manter_peso"

# Modelos para Dieta

class FoodItem(BaseModel):
    """Item de alimento em uma refeição"""
    food_id: str
    name: str
    quantity: float = Field(..., gt=0)
    unit: str  # gramas, ml, unidade, etc.
    calories: float = Field(..., ge=0)
    protein: float = Field(..., ge=0)
    carbs: float = Field(..., ge=0)
    fat: float = Field(..., ge=0)
    fiber: Optional[float] = Field(None, ge=0)
    sodium: Optional[float] = Field(None, ge=0)

class Meal(BaseModel):
    """Refeição completa"""
    meal_type: MealType
    name: str
    time_suggestion: Optional[time] = None
    foods: List[FoodItem]
    total_calories: float = Field(..., ge=0)
    total_protein: float = Field(..., ge=0)
    total_carbs: float = Field(..., ge=0)
    total_fat: float = Field(..., ge=0)
    preparation_time: Optional[int] = Field(None, ge=0)  # minutos
    instructions: Optional[str] = None
    tips: Optional[List[str]] = None

class DietPlan(BaseModel):
    """Plano de dieta diário"""
    user_id: str
    date: date
    goal: GoalType
    target_calories: float = Field(..., gt=0)
    target_protein: float = Field(..., ge=0)
    target_carbs: float = Field(..., ge=0)
    target_fat: float = Field(..., ge=0)
    meals: List[Meal]
    total_calories: float = Field(..., ge=0)
    total_protein: float = Field(..., ge=0)
    total_carbs: float = Field(..., ge=0)
    total_fat: float = Field(..., ge=0)
    water_intake_ml: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

# Modelos para Treino

class ExerciseSet(BaseModel):
    """Série de um exercício"""
    set_number: int = Field(..., ge=1)
    reps: Optional[int] = Field(None, ge=1)
    weight: Optional[float] = Field(None, ge=0)  # kg
    duration: Optional[int] = Field(None, ge=0)  # segundos
    distance: Optional[float] = Field(None, ge=0)  # metros
    rest_seconds: int = Field(..., ge=0)
    notes: Optional[str] = None
    completed: bool = False
    performance_rating: Optional[int] = Field(None, ge=1, le=5)

class Exercise(BaseModel):
    """Exercício individual"""
    exercise_id: str
    name: str
    muscle_groups: List[str]
    equipment: Optional[str] = None
    difficulty: DifficultyLevel
    sets: List[ExerciseSet]
    instructions: Optional[str] = None
    tips: Optional[List[str]] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    safety_notes: Optional[List[str]] = None

class WarmupExercise(BaseModel):
    """Exercício de aquecimento"""
    name: str
    duration_seconds: int = Field(..., gt=0)
    instructions: str
    video_url: Optional[str] = None

class Warmup(BaseModel):
    """Aquecimento completo"""
    total_duration_minutes: int = Field(..., gt=0)
    exercises: List[WarmupExercise]
    notes: Optional[str] = None

class WorkoutSession(BaseModel):
    """Sessão de treino"""
    session_id: str
    name: str
    workout_type: WorkoutType
    muscle_groups_focus: List[str]
    difficulty: DifficultyLevel
    estimated_duration_minutes: int = Field(..., gt=0)
    warmup: Optional[Warmup] = None
    exercises: List[Exercise]
    cooldown_notes: Optional[str] = None
    equipment_needed: List[str] = []
    location: str = "gym"  # gym, home, outdoor
    notes: Optional[str] = None

class WorkoutPlan(BaseModel):
    """Plano de treino diário"""
    user_id: str
    date: date
    goal: GoalType
    sessions: List[WorkoutSession]
    total_estimated_duration_minutes: int = Field(..., ge=0)
    rest_day: bool = False
    active_recovery: Optional[str] = None
    last_performance: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

# Modelos para Apresentação

class ProgressMetric(BaseModel):
    """Métrica de progresso"""
    metric_name: str
    current_value: float
    target_value: Optional[float] = None
    unit: str
    trend: Optional[str] = None  # "up", "down", "stable"
    percentage_change: Optional[float] = None

class DailyTip(BaseModel):
    """Dica diária"""
    category: str  # nutrition, training, lifestyle, motivation
    title: str
    content: str
    priority: int = Field(default=1, ge=1, le=5)

class PlanPresentation(BaseModel):
    """Apresentação personalizada do plano"""
    user_id: str
    date: date
    user_name: Optional[str] = None
    goal: GoalType
    motivational_message: str
    daily_summary: str
    diet_highlights: List[str]
    workout_highlights: List[str]
    progress_metrics: List[ProgressMetric]
    daily_tips: List[DailyTip]
    weekly_progress_summary: Optional[str] = None
    next_milestone: Optional[str] = None
    encouragement_note: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Modelos para Resumo Semanal

class WeeklyMealSummary(BaseModel):
    """Resumo semanal de refeições"""
    total_meals: int
    avg_calories_per_day: float
    avg_protein_per_day: float
    avg_carbs_per_day: float
    avg_fat_per_day: float
    most_consumed_foods: List[str]
    meal_variety_score: float = Field(..., ge=0, le=10)

class WeeklyWorkoutSummary(BaseModel):
    """Resumo semanal de treinos"""
    total_workouts: int
    total_duration_minutes: int
    avg_duration_per_workout: float
    muscle_groups_trained: List[str]
    workout_types_distribution: Dict[str, int]
    completion_rate: float = Field(..., ge=0, le=1)
    performance_trend: Optional[str] = None

class WeeklySchedule(BaseModel):
    """Cronograma semanal completo"""
    user_id: str
    week_start_date: date
    goal: GoalType
    diet_summary: WeeklyMealSummary
    workout_summary: WeeklyWorkoutSummary
    total_target_calories: float
    total_actual_calories: Optional[float] = None
    adherence_rate: Optional[float] = Field(None, ge=0, le=1)
    weekly_goals: List[str]
    achievements: List[str]
    areas_for_improvement: List[str]
    next_week_focus: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Modelos para Configuração de Algoritmos

class DietPreferences(BaseModel):
    """Preferências de dieta do usuário"""
    style: str = "varied"  # "consistent" ou "varied"
    meal_frequency: int = Field(default=6, ge=3, le=8)
    dietary_restrictions: List[str] = []
    allergies: List[str] = []
    disliked_foods: List[str] = []
    preferred_foods: List[str] = []
    cooking_time_preference: str = "medium"  # "quick", "medium", "elaborate"
    budget_level: str = "medium"  # "low", "medium", "high"

class WorkoutPreferences(BaseModel):
    """Preferências de treino do usuário"""
    available_days: List[str]  # ["monday", "tuesday", ...]
    session_duration_preference: int = Field(default=60, ge=15, le=180)  # minutos
    location: str = "gym"  # "gym", "home", "outdoor"
    equipment_available: List[str] = []
    preferred_workout_times: List[str] = []  # ["morning", "afternoon", "evening"]
    intensity_preference: str = "medium"  # "low", "medium", "high"
    focus_areas: List[str] = []  # grupos musculares prioritários

class AlgorithmConfig(BaseModel):
    """Configuração para algoritmos de geração"""
    user_id: str
    goal: GoalType
    experience_level: DifficultyLevel
    diet_preferences: DietPreferences
    workout_preferences: WorkoutPreferences
    target_calories: float = Field(..., gt=0)
    target_protein: float = Field(..., ge=0)
    target_carbs: float = Field(..., ge=0)
    target_fat: float = Field(..., ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

# Modelos de Resposta da API

class DietPlanResponse(BaseModel):
    """Resposta da API para plano de dieta"""
    success: bool = True
    data: DietPlan
    message: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkoutPlanResponse(BaseModel):
    """Resposta da API para plano de treino"""
    success: bool = True
    data: WorkoutPlan
    message: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class PresentationResponse(BaseModel):
    """Resposta da API para apresentação"""
    success: bool = True
    data: PlanPresentation
    message: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class WeeklyScheduleResponse(BaseModel):
    """Resposta da API para cronograma semanal"""
    success: bool = True
    data: WeeklySchedule
    message: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Resposta de erro da API"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


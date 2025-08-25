"""
Modelos de dados para usuários
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, validator, Field
from enum import Enum

class Gender(str, Enum):
    """Gênero do usuário"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class ActivityLevel(str, Enum):
    """Nível de atividade física"""
    SEDENTARY = "sedentario"
    LIGHTLY_ACTIVE = "levemente_ativo"
    MODERATELY_ACTIVE = "moderadamente_ativo"
    VERY_ACTIVE = "muito_ativo"
    EXTREMELY_ACTIVE = "extremamente_ativo"

class FitnessGoal(str, Enum):
    """Objetivos fitness"""
    LOSE_WEIGHT = "perder_peso"
    GAIN_MUSCLE = "ganhar_massa"
    MAINTAIN_WEIGHT = "manter_peso"
    IMPROVE_HEALTH = "melhorar_saude"
    INCREASE_STRENGTH = "aumentar_forca"
    IMPROVE_ENDURANCE = "melhorar_resistencia"

class TrainingExperience(str, Enum):
    """Experiência com treinamento"""
    BEGINNER = "iniciante"
    INTERMEDIATE = "intermediario"
    ADVANCED = "avancado"
    EXPERT = "expert"

class BodyComposition(str, Enum):
    """Composição corporal"""
    VERY_LOW = "muito_baixo"
    LOW = "baixo"
    NORMAL = "normal"
    HIGH = "alto"
    VERY_HIGH = "muito_alto"

class UserRegistration(BaseModel):
    """Dados para registro de usuário"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    gender: Gender
    terms_accepted: bool = True
    privacy_accepted: bool = True
    marketing_consent: Optional[bool] = False
    
    @validator('password')
    def validate_password(cls, v):
        """Validar força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError('Senha deve conter ao menos: 1 maiúscula, 1 minúscula, 1 número e 1 caractere especial')
        
        return v
    
    @validator('date_of_birth')
    def validate_age(cls, v):
        """Validar idade mínima"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 13:
            raise ValueError('Usuário deve ter pelo menos 13 anos')
        if age > 120:
            raise ValueError('Idade inválida')
        
        return v

class SocialLogin(BaseModel):
    """Dados para login social"""
    provider: str = Field(..., pattern="^(google|apple|facebook)$")
    token: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    profile_picture: Optional[str] = None

class HealthAssessment(BaseModel):
    """Avaliação de saúde"""
    height: float = Field(..., gt=0, le=300, description="Altura em cm")
    weight: float = Field(..., gt=0, le=500, description="Peso em kg")
    body_fat_percentage: Optional[float] = Field(None, ge=3, le=50, description="% de gordura corporal")
    muscle_mass: Optional[float] = Field(None, gt=0, description="Massa muscular em kg")
    
    # Medidas corporais
    waist_circumference: Optional[float] = Field(None, gt=0, le=200, description="Circunferência da cintura em cm")
    hip_circumference: Optional[float] = Field(None, gt=0, le=200, description="Circunferência do quadril em cm")
    chest_circumference: Optional[float] = Field(None, gt=0, le=200, description="Circunferência do peito em cm")
    arm_circumference: Optional[float] = Field(None, gt=0, le=100, description="Circunferência do braço em cm")
    thigh_circumference: Optional[float] = Field(None, gt=0, le=100, description="Circunferência da coxa em cm")
    
    # Pressão arterial
    systolic_pressure: Optional[int] = Field(None, ge=70, le=250, description="Pressão sistólica")
    diastolic_pressure: Optional[int] = Field(None, ge=40, le=150, description="Pressão diastólica")
    
    # Frequência cardíaca
    resting_heart_rate: Optional[int] = Field(None, ge=30, le=200, description="FC de repouso")
    max_heart_rate: Optional[int] = Field(None, ge=100, le=250, description="FC máxima")
    
    @validator('body_fat_percentage')
    def validate_body_fat(cls, v, values):
        """Validar % de gordura baseado no gênero"""
        if v is None:
            return v
        
        # Valores típicos: Homens 3-25%, Mulheres 10-35%
        if v < 3 or v > 50:
            raise ValueError('Percentual de gordura corporal deve estar entre 3% e 50%')
        
        return v

class MedicalHistory(BaseModel):
    """Histórico médico"""
    has_diabetes: bool = False
    has_hypertension: bool = False
    has_heart_disease: bool = False
    has_thyroid_issues: bool = False
    has_joint_problems: bool = False
    has_back_problems: bool = False
    has_allergies: bool = False
    
    medications: List[str] = Field(default_factory=list, description="Medicamentos em uso")
    supplements: List[str] = Field(default_factory=list, description="Suplementos em uso")
    allergies: List[str] = Field(default_factory=list, description="Alergias conhecidas")
    
    recent_injuries: Optional[str] = Field(None, description="Lesões recentes")
    surgery_history: Optional[str] = Field(None, description="Histórico de cirurgias")
    
    doctor_clearance: bool = Field(False, description="Liberação médica para exercícios")
    last_checkup: Optional[date] = Field(None, description="Último check-up médico")

class LifestyleAssessment(BaseModel):
    """Avaliação de estilo de vida"""
    occupation: str = Field(..., description="Profissão/ocupação")
    work_activity_level: ActivityLevel = Field(..., description="Nível de atividade no trabalho")
    leisure_activity_level: ActivityLevel = Field(..., description="Nível de atividade no lazer")
    
    sleep_hours: float = Field(..., ge=3, le=12, description="Horas de sono por noite")
    sleep_quality: int = Field(..., ge=1, le=10, description="Qualidade do sono (1-10)")
    
    stress_level: int = Field(..., ge=1, le=10, description="Nível de estresse (1-10)")
    
    smoking: bool = False
    alcohol_consumption: str = Field("nunca", pattern="^(nunca|raramente|moderadamente|frequentemente)$")
    
    water_intake: float = Field(..., ge=0, le=10, description="Litros de água por dia")
    
    # Hábitos alimentares
    meals_per_day: int = Field(..., ge=1, le=10, description="Refeições por dia")
    snacks_frequency: str = Field("raramente", pattern="^(nunca|raramente|moderadamente|frequentemente)$")
    
    # Disponibilidade para treino
    available_days_per_week: int = Field(..., ge=1, le=7, description="Dias disponíveis para treino")
    preferred_workout_time: str = Field("manha", pattern="^(manha|tarde|noite|flexivel)$")
    workout_duration_preference: int = Field(..., ge=15, le=180, description="Duração preferida do treino em minutos")

class FitnessGoals(BaseModel):
    """Objetivos fitness"""
    primary_goal: FitnessGoal
    secondary_goals: List[FitnessGoal] = Field(default_factory=list)
    
    target_weight: Optional[float] = Field(None, gt=0, le=500, description="Peso alvo em kg")
    target_body_fat: Optional[float] = Field(None, ge=3, le=50, description="% gordura alvo")
    target_muscle_mass: Optional[float] = Field(None, gt=0, description="Massa muscular alvo")
    
    timeline_weeks: int = Field(..., ge=1, le=104, description="Prazo em semanas")
    
    # Preferências de treino
    training_experience: TrainingExperience
    preferred_training_types: List[str] = Field(default_factory=list, description="Tipos de treino preferidos")
    equipment_available: List[str] = Field(default_factory=list, description="Equipamentos disponíveis")
    
    # Limitações
    physical_limitations: List[str] = Field(default_factory=list, description="Limitações físicas")
    exercise_restrictions: List[str] = Field(default_factory=list, description="Exercícios a evitar")

class UserPreferences(BaseModel):
    """Preferências do usuário"""
    language: str = Field("pt-BR", description="Idioma preferido")
    timezone: str = Field("America/Sao_Paulo", description="Fuso horário")
    units: str = Field("metric", pattern="^(metric|imperial)$", description="Sistema de medidas")
    
    # Notificações
    email_notifications: bool = True
    push_notifications: bool = True
    workout_reminders: bool = True
    progress_updates: bool = True
    
    # Privacidade
    profile_visibility: str = Field("private", pattern="^(public|friends|private)$")
    share_progress: bool = False
    
    # Conteúdo
    content_difficulty: str = Field("intermediate", pattern="^(beginner|intermediate|advanced)$")
    show_premium_content: bool = True

class OnboardingData(BaseModel):
    """Dados completos do onboarding"""
    health_assessment: HealthAssessment
    medical_history: MedicalHistory
    lifestyle_assessment: LifestyleAssessment
    fitness_goals: FitnessGoals
    preferences: UserPreferences
    
    # Metadados
    completed_at: Optional[datetime] = None
    version: str = "1.0"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class CalorieCalculation(BaseModel):
    """Resultado do cálculo calórico"""
    bmr: float = Field(..., description="Taxa Metabólica Basal")
    tdee: float = Field(..., description="Gasto Energético Total Diário")
    
    # Fatores aplicados
    body_composition_factor: float = 1.0
    pharma_factor: float = 1.0
    training_experience_factor: float = 1.0
    activity_factor: float = 1.2
    
    # Metas calóricas
    maintenance_calories: float
    cutting_calories: float
    bulking_calories: float
    
    # Macronutrientes (gramas)
    protein_grams: float
    carbs_grams: float
    fat_grams: float
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    formula_used: str = "mifflin_st_jeor"

class UserProfile(BaseModel):
    """Perfil completo do usuário"""
    id: str
    email: EmailStr
    name: str
    date_of_birth: date
    gender: Gender
    
    # Status
    is_active: bool = True
    is_verified: bool = False
    is_premium: bool = False
    
    # Onboarding
    onboarding_completed: bool = False
    onboarding_data: Optional[OnboardingData] = None
    
    # Cálculos
    calorie_calculation: Optional[CalorieCalculation] = None
    
    # Metadados
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Fotos
    profile_picture: Optional[str] = None
    progress_photos: List[str] = Field(default_factory=list)

class UserResponse(BaseModel):
    """Resposta com dados do usuário (sem dados sensíveis)"""
    id: str
    email: EmailStr
    name: str
    date_of_birth: date
    gender: Gender
    is_active: bool
    is_verified: bool
    is_premium: bool
    onboarding_completed: bool
    profile_picture: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

class AuthTokens(BaseModel):
    """Tokens de autenticação"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class AuthResponse(BaseModel):
    """Resposta de autenticação"""
    user: UserResponse
    tokens: AuthTokens
    message: str = "Login realizado com sucesso"


"""
Modelos de dados para o Tracking Service
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid


class LogType(str, Enum):
    """Tipos de log disponíveis"""
    MEAL_CHECKIN = "meal_checkin"
    SET = "set"
    BODY_WEIGHT = "body_weight"
    WORKOUT_SESSION = "workout_session"
    WATER_INTAKE = "water_intake"
    SLEEP = "sleep"
    MOOD = "mood"


class TrendDirection(str, Enum):
    """Direção da tendência"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


# Modelos de entrada (requests)

class MealCheckinRequest(BaseModel):
    """Request para check-in de refeição"""
    meal_type: str = Field(..., description="Tipo da refeição (cafe_da_manha, almoco, etc.)")
    foods_consumed: List[Dict[str, Any]] = Field(..., description="Lista de alimentos consumidos")
    total_calories: float = Field(..., gt=0, description="Total de calorias da refeição")
    total_protein: float = Field(..., ge=0, description="Total de proteína em gramas")
    total_carbs: float = Field(..., ge=0, description="Total de carboidratos em gramas")
    total_fat: float = Field(..., ge=0, description="Total de gordura em gramas")
    notes: Optional[str] = Field(None, description="Notas adicionais")


class SetRequest(BaseModel):
    """Request para registro de série de treino"""
    exercise_id: str = Field(..., description="ID do exercício")
    exercise_name: str = Field(..., description="Nome do exercício")
    weight_kg: Optional[float] = Field(None, ge=0, description="Peso utilizado em kg")
    reps_done: int = Field(..., gt=0, le=100, description="Repetições realizadas")
    set_number: int = Field(..., gt=0, description="Número da série")
    rpe: Optional[int] = Field(None, ge=1, le=10, description="Rate of Perceived Exertion (1-10)")
    notes: Optional[str] = Field(None, description="Notas sobre a série")


class BodyWeightRequest(BaseModel):
    """Request para registro de peso corporal"""
    weight_kg: float = Field(..., gt=30, lt=300, description="Peso em kg")
    body_fat_percentage: Optional[float] = Field(None, ge=0, le=50, description="Percentual de gordura corporal")
    muscle_mass_kg: Optional[float] = Field(None, ge=0, description="Massa muscular em kg")
    notes: Optional[str] = Field(None, description="Notas sobre a medição")


class WorkoutSessionEndRequest(BaseModel):
    """Request para finalização de sessão de treino"""
    session_id: str = Field(..., description="ID da sessão de treino")
    duration_minutes: int = Field(..., gt=0, le=300, description="Duração do treino em minutos")
    exercises_performed: List[str] = Field(..., description="Lista de IDs dos exercícios realizados")
    perceived_intensity: Optional[int] = Field(None, ge=1, le=10, description="Intensidade percebida (1-10)")
    notes: Optional[str] = Field(None, description="Notas sobre o treino")


# Modelos de dados internos

class DailyLog(BaseModel):
    """Modelo para logs diários"""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único do log")
    user_id: str = Field(..., description="ID do usuário")
    log_type: LogType = Field(..., description="Tipo do log")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp do log")
    date: date = Field(default_factory=date.today, description="Data do log")
    value: Dict[str, Any] = Field(..., description="Dados específicos do log")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados adicionais")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


# Modelos de resposta (dashboard)

class NutritionalSummary(BaseModel):
    """Resumo nutricional do dia"""
    calories_consumed: float = Field(0, description="Calorias consumidas")
    calories_target: float = Field(0, description="Meta de calorias")
    calories_remaining: float = Field(0, description="Calorias restantes")
    protein_consumed: float = Field(0, description="Proteína consumida (g)")
    protein_target: float = Field(0, description="Meta de proteína (g)")
    carbs_consumed: float = Field(0, description="Carboidratos consumidos (g)")
    carbs_target: float = Field(0, description="Meta de carboidratos (g)")
    fat_consumed: float = Field(0, description="Gordura consumida (g)")
    fat_target: float = Field(0, description="Meta de gordura (g)")
    water_consumed_ml: float = Field(0, description="Água consumida (ml)")
    water_target_ml: float = Field(0, description="Meta de água (ml)")
    meals_completed: int = Field(0, description="Refeições completadas")
    total_meals: int = Field(0, description="Total de refeições planejadas")


class WorkoutSummary(BaseModel):
    """Resumo de treino do dia"""
    workout_planned: bool = Field(False, description="Se há treino planejado")
    workout_completed: bool = Field(False, description="Se o treino foi completado")
    workout_name: Optional[str] = Field(None, description="Nome do treino")
    duration_planned_minutes: int = Field(0, description="Duração planejada (min)")
    duration_actual_minutes: int = Field(0, description="Duração real (min)")
    calories_burned: float = Field(0, description="Calorias queimadas")
    exercises_completed: int = Field(0, description="Exercícios completados")
    total_exercises: int = Field(0, description="Total de exercícios planejados")
    muscle_groups_focus: List[str] = Field(default_factory=list, description="Grupos musculares trabalhados")


class EnergyBalance(BaseModel):
    """Balanço energético do dia"""
    calories_in: float = Field(0, description="Calorias consumidas")
    calories_out: float = Field(0, description="Calorias gastas")
    net_balance: float = Field(0, description="Balanço líquido")
    bmr: float = Field(0, description="Taxa metabólica basal")
    activity_calories: float = Field(0, description="Calorias de atividade")
    exercise_calories: float = Field(0, description="Calorias de exercício")
    balance_status: str = Field("neutral", description="Status do balanço (deficit/surplus/neutral)")


class ProgressMetric(BaseModel):
    """Métrica de progresso"""
    metric_name: str = Field(..., description="Nome da métrica")
    current_value: float = Field(..., description="Valor atual")
    previous_value: Optional[float] = Field(None, description="Valor anterior")
    change_value: Optional[float] = Field(None, description="Mudança absoluta")
    change_percentage: Optional[float] = Field(None, description="Mudança percentual")
    trend: TrendDirection = Field(TrendDirection.STABLE, description="Direção da tendência")
    unit: str = Field(..., description="Unidade de medida")
    last_updated: datetime = Field(..., description="Última atualização")


class DashboardResponse(BaseModel):
    """Resposta do dashboard principal"""
    user_id: str = Field(..., description="ID do usuário")
    user_name: Optional[str] = Field(None, description="Nome/nickname do usuário")
    date: date = Field(..., description="Data do dashboard")
    nutritional_summary: NutritionalSummary = Field(..., description="Resumo nutricional")
    workout_summary: WorkoutSummary = Field(..., description="Resumo de treino")
    energy_balance: EnergyBalance = Field(..., description="Balanço energético")
    progress_highlights: List[ProgressMetric] = Field(default_factory=list, description="Destaques de progresso")
    daily_streak: int = Field(0, description="Sequência de dias seguindo o plano")
    motivation_message: Optional[str] = Field(None, description="Mensagem motivacional")
    next_milestone: Optional[str] = Field(None, description="Próximo marco")
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


# Modelos para analytics de progresso

class WeightDataPoint(BaseModel):
    """Ponto de dados de peso"""
    date: date = Field(..., description="Data da medição")
    weight_kg: float = Field(..., description="Peso em kg")
    body_fat_percentage: Optional[float] = Field(None, description="Percentual de gordura")
    muscle_mass_kg: Optional[float] = Field(None, description="Massa muscular")


class StrengthDataPoint(BaseModel):
    """Ponto de dados de força"""
    date: date = Field(..., description="Data do treino")
    exercise_id: str = Field(..., description="ID do exercício")
    exercise_name: str = Field(..., description="Nome do exercício")
    max_weight_kg: float = Field(..., description="Peso máximo levantado")
    total_volume_kg: float = Field(..., description="Volume total (peso x reps x séries)")
    one_rep_max_estimated: Optional[float] = Field(None, description="1RM estimado")


class ProgressChart(BaseModel):
    """Dados para gráfico de progresso"""
    chart_type: str = Field(..., description="Tipo do gráfico (weight/strength/volume)")
    title: str = Field(..., description="Título do gráfico")
    x_axis_label: str = Field(..., description="Label do eixo X")
    y_axis_label: str = Field(..., description="Label do eixo Y")
    data_points: List[Dict[str, Any]] = Field(..., description="Pontos de dados")
    trend_line: Optional[List[Dict[str, Any]]] = Field(None, description="Linha de tendência")
    annotations: List[Dict[str, Any]] = Field(default_factory=list, description="Anotações no gráfico")


class ProgressSummaryResponse(BaseModel):
    """Resposta do resumo de progresso"""
    user_id: str = Field(..., description="ID do usuário")
    period_start: date = Field(..., description="Início do período")
    period_end: date = Field(..., description="Fim do período")
    weight_progress: List[WeightDataPoint] = Field(default_factory=list, description="Progresso de peso")
    strength_progress: List[StrengthDataPoint] = Field(default_factory=list, description="Progresso de força")
    charts: List[ProgressChart] = Field(default_factory=list, description="Gráficos de progresso")
    key_metrics: List[ProgressMetric] = Field(default_factory=list, description="Métricas principais")
    achievements: List[str] = Field(default_factory=list, description="Conquistas do período")
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


# Modelos de resposta padrão

class SuccessResponse(BaseModel):
    """Resposta de sucesso padrão"""
    success: bool = Field(True, description="Indica sucesso da operação")
    message: str = Field(..., description="Mensagem de sucesso")
    data: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da resposta")


class ErrorResponse(BaseModel):
    """Resposta de erro padrão"""
    success: bool = Field(False, description="Indica falha da operação")
    error_code: str = Field(..., description="Código do erro")
    message: str = Field(..., description="Mensagem de erro")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da resposta")


# Modelos de configuração

class ServiceHealthCheck(BaseModel):
    """Status de saúde do serviço"""
    service_name: str = Field(..., description="Nome do serviço")
    status: str = Field(..., description="Status (healthy/unhealthy)")
    version: str = Field(..., description="Versão do serviço")
    uptime_seconds: float = Field(..., description="Tempo de atividade em segundos")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Status das dependências")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp do check")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


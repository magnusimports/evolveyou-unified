"""
Modelos de dados para exercícios
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    """Níveis de dificuldade"""
    INICIANTE = "iniciante"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"

class ExerciseType(str, Enum):
    """Tipos de exercício"""
    FORCA = "forca"
    CARDIO = "cardio"
    FLEXIBILIDADE = "flexibilidade"
    EQUILIBRIO = "equilibrio"
    FUNCIONAL = "funcional"

class Equipment(str, Enum):
    """Equipamentos"""
    PESO_CORPORAL = "peso_corporal"
    HALTERES = "halteres"
    BARRA = "barra"
    KETTLEBELL = "kettlebell"
    ELASTICO = "elastico"
    MAQUINA = "maquina"
    CABO = "cabo"
    MEDICINE_BALL = "medicine_ball"
    BANCO = "banco"
    STEP = "step"
    CORDA = "corda"
    OUTROS = "outros"

class MuscleGroup(str, Enum):
    """Grupos musculares"""
    PEITO = "peito"
    COSTAS = "costas"
    OMBROS = "ombros"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    ANTEBRACO = "antebraco"
    CORE = "core"
    QUADRICEPS = "quadriceps"
    ISQUIOTIBIAIS = "isquiotibiais"
    GLUTEOS = "gluteos"
    PANTURRILHAS = "panturrilhas"
    CORPO_TODO = "corpo_todo"

class PremiumGuidance(BaseModel):
    """Orientações premium para exercícios"""
    form_tips: List[str] = Field(default_factory=list, description="Dicas de execução")
    common_mistakes: List[str] = Field(default_factory=list, description="Erros comuns")
    breathing_pattern: Optional[str] = Field(None, description="Padrão respiratório")
    progression_tips: List[str] = Field(default_factory=list, description="Dicas de progressão")
    regression_options: List[str] = Field(default_factory=list, description="Opções de regressão")
    safety_notes: List[str] = Field(default_factory=list, description="Notas de segurança")
    muscle_activation_cues: List[str] = Field(default_factory=list, description="Dicas de ativação muscular")

class ExerciseVariation(BaseModel):
    """Variação de um exercício"""
    name: str = Field(..., description="Nome da variação")
    description: str = Field(..., description="Descrição da variação")
    difficulty_modifier: int = Field(0, description="Modificador de dificuldade (-2 a +2)")
    equipment_changes: Optional[List[Equipment]] = Field(None, description="Mudanças de equipamento")

class Exercise(BaseModel):
    """Modelo de dados para exercícios"""
    id: Optional[str] = Field(None, description="ID único do exercício")
    name: str = Field(..., description="Nome do exercício")
    name_en: Optional[str] = Field(None, description="Nome em inglês")
    
    # Classificação
    primary_muscle_group: MuscleGroup = Field(..., description="Grupo muscular principal")
    secondary_muscle_groups: List[MuscleGroup] = Field(default_factory=list, description="Grupos musculares secundários")
    exercise_type: ExerciseType = Field(..., description="Tipo de exercício")
    equipment: List[Equipment] = Field(..., description="Equipamentos necessários")
    difficulty: DifficultyLevel = Field(..., description="Nível de dificuldade")
    
    # Descrição e instruções
    description: str = Field(..., description="Descrição do exercício")
    instructions: List[str] = Field(..., description="Instruções passo a passo")
    
    # Orientações premium
    premium_guidance: Optional[PremiumGuidance] = Field(None, description="Orientações premium")
    
    # Variações
    variations: List[ExerciseVariation] = Field(default_factory=list, description="Variações do exercício")
    
    # Métricas
    met_value: Optional[float] = Field(None, description="Valor MET para cálculo calórico")
    duration_minutes: Optional[int] = Field(None, description="Duração recomendada em minutos")
    
    # Metadados
    tags: List[str] = Field(default_factory=list, description="Tags para busca")
    video_url: Optional[str] = Field(None, description="URL do vídeo demonstrativo")
    image_urls: List[str] = Field(default_factory=list, description="URLs das imagens")
    
    # Informações de origem
    source: Optional[str] = Field(None, description="Fonte dos dados")
    verified: bool = Field(False, description="Se os dados foram verificados")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ExerciseSearchResponse(BaseModel):
    """Resposta da busca de exercícios"""
    exercises: List[Exercise] = Field(..., description="Lista de exercícios encontrados")
    total: int = Field(..., description="Total de resultados disponíveis")
    limit: int = Field(..., description="Limite aplicado na busca")
    offset: int = Field(..., description="Offset aplicado na busca")
    has_more: bool = Field(..., description="Se há mais resultados disponíveis")

class METValue(BaseModel):
    """Valor MET para cálculo de gasto calórico"""
    activity: str = Field(..., description="Nome da atividade")
    met_value: float = Field(..., description="Valor MET")
    exercise_type: ExerciseType = Field(..., description="Tipo de exercício")
    intensity: Optional[str] = Field(None, description="Intensidade da atividade")
    description: Optional[str] = Field(None, description="Descrição da atividade")

class ExerciseCreateRequest(BaseModel):
    """Request para criar um novo exercício"""
    name: str = Field(..., description="Nome do exercício")
    primary_muscle_group: MuscleGroup = Field(..., description="Grupo muscular principal")
    exercise_type: ExerciseType = Field(..., description="Tipo de exercício")
    equipment: List[Equipment] = Field(..., description="Equipamentos necessários")
    difficulty: DifficultyLevel = Field(..., description="Nível de dificuldade")
    description: str = Field(..., description="Descrição do exercício")
    instructions: List[str] = Field(..., description="Instruções passo a passo")
    
    # Campos opcionais
    name_en: Optional[str] = None
    secondary_muscle_groups: Optional[List[MuscleGroup]] = None
    premium_guidance: Optional[PremiumGuidance] = None
    variations: Optional[List[ExerciseVariation]] = None
    met_value: Optional[float] = None
    duration_minutes: Optional[int] = None
    tags: Optional[List[str]] = None
    video_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    source: Optional[str] = None

class ExerciseUpdateRequest(BaseModel):
    """Request para atualizar um exercício"""
    name: Optional[str] = None
    primary_muscle_group: Optional[MuscleGroup] = None
    secondary_muscle_groups: Optional[List[MuscleGroup]] = None
    exercise_type: Optional[ExerciseType] = None
    equipment: Optional[List[Equipment]] = None
    difficulty: Optional[DifficultyLevel] = None
    description: Optional[str] = None
    instructions: Optional[List[str]] = None
    premium_guidance: Optional[PremiumGuidance] = None
    variations: Optional[List[ExerciseVariation]] = None
    met_value: Optional[float] = None
    duration_minutes: Optional[int] = None
    tags: Optional[List[str]] = None
    video_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    verified: Optional[bool] = None


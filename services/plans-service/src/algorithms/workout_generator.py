"""
Algoritmo de Geração de Treino Personalizado
"""

import random
import math
from datetime import date, datetime, timedelta, time
from typing import List, Dict, Optional, Tuple, Set
import structlog
from dataclasses import dataclass
from enum import Enum

from models.plan import (
    WorkoutPlan, WorkoutSession, Exercise, ExerciseSet, Warmup, WarmupExercise,
    WorkoutType, DifficultyLevel, GoalType, WorkoutPreferences, AlgorithmConfig
)
from config.settings import get_settings

logger = structlog.get_logger(__name__)

class MuscleGroup(str, Enum):
    """Grupos musculares"""
    PEITO = "peito"
    COSTAS = "costas"
    OMBROS = "ombros"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    QUADRICEPS = "quadriceps"
    POSTERIOR = "posterior"
    GLUTEOS = "gluteos"
    PANTURRILHAS = "panturrilhas"
    CORE = "core"
    ANTEBRACOS = "antebracos"

class TrainingSplit(str, Enum):
    """Tipos de divisão de treino"""
    FULL_BODY = "full_body"
    UPPER_LOWER = "upper_lower"
    PUSH_PULL_LEGS = "push_pull_legs"
    UPPER_LOWER_PUSH_PULL = "upper_lower_push_pull"
    PUSH_PULL_LEGS_UPPER_LOWER = "push_pull_legs_upper_lower"
    PUSH_PULL_LEGS_PUSH_PULL_LEGS = "push_pull_legs_push_pull_legs"
    DAILY_SPECIALIZATION = "daily_specialization"

@dataclass
class ExerciseCandidate:
    """Candidato a exercício para o treino"""
    exercise_id: str
    name: str
    muscle_groups: List[str]
    primary_muscle: str
    secondary_muscles: List[str]
    equipment: str
    difficulty: DifficultyLevel
    movement_pattern: str  # compound, isolation, cardio
    safety_rating: float  # 0-1
    effectiveness_rating: float  # 0-1
    location_compatibility: List[str]  # gym, home, outdoor
    time_efficiency: float  # 0-1

@dataclass
class WorkoutTemplate:
    """Template de treino para um dia específico"""
    name: str
    muscle_groups_focus: List[str]
    workout_type: WorkoutType
    target_duration_minutes: int
    exercise_slots: List[Dict]  # Slots para exercícios com critérios
    warmup_type: str
    intensity_level: float  # 0-1

class WorkoutGenerator:
    """Gerador de planos de treino personalizados"""
    
    def __init__(self, content_service, firebase_service):
        self.content_service = content_service
        self.firebase_service = firebase_service
        self.settings = get_settings()
        self.workout_config = self.settings.workout_algorithm_config
        
        # Definir splits de treino
        self.training_splits = {
            1: self._create_full_body_split(),
            2: self._create_upper_lower_split(),
            3: self._create_push_pull_legs_split(),
            4: self._create_upper_lower_push_pull_split(),
            5: self._create_push_pull_legs_upper_lower_split(),
            6: self._create_push_pull_legs_x2_split(),
            7: self._create_daily_specialization_split()
        }
    
    async def generate_workout_plan(
        self, 
        user_id: str, 
        target_date: date,
        algorithm_config: AlgorithmConfig
    ) -> WorkoutPlan:
        """
        Gera um plano de treino personalizado para o usuário
        
        Args:
            user_id: ID do usuário
            target_date: Data alvo para o plano
            algorithm_config: Configuração do algoritmo
            
        Returns:
            WorkoutPlan: Plano de treino completo
        """
        logger.info("Iniciando geração de plano de treino", 
                   user_id=user_id, date=target_date)
        
        try:
            # 1. Verificar se já existe plano para a data
            existing_plan = await self._get_existing_plan(user_id, target_date)
            if existing_plan and not self._should_regenerate_plan(existing_plan, algorithm_config):
                logger.info("Plano de treino existente encontrado", user_id=user_id)
                return existing_plan
            
            # 2. Obter dados do usuário e preferências
            user_data = await self._get_user_data(user_id)
            workout_preferences = algorithm_config.workout_preferences
            
            # 3. Determinar se é dia de treino ou descanso
            is_rest_day = self._is_rest_day(target_date, workout_preferences)
            
            if is_rest_day:
                return await self._create_rest_day_plan(user_id, target_date, algorithm_config)
            
            # 4. Selecionar split de treino baseado nos dias disponíveis
            available_days = len(workout_preferences.available_days)
            split_templates = self.training_splits.get(available_days, self.training_splits[3])
            
            # 5. Determinar qual template usar para este dia
            day_of_week = target_date.strftime("%A").lower()
            workout_template = self._select_template_for_day(day_of_week, split_templates, workout_preferences)
            
            # 6. Obter exercícios disponíveis do Content Service
            available_exercises = await self._get_available_exercises(workout_preferences)
            
            # 7. Gerar sessões de treino
            sessions = []
            if workout_template:
                session = await self._generate_workout_session(
                    workout_template, available_exercises, algorithm_config, user_data
                )
                sessions.append(session)
            
            # 8. Calcular duração total
            total_duration = sum(session.estimated_duration_minutes for session in sessions)
            
            # 9. Obter dados de performance anterior
            last_performance = await self._get_last_performance(user_id, workout_template.name if workout_template else "")
            
            # 10. Criar plano final
            workout_plan = WorkoutPlan(
                user_id=user_id,
                date=target_date,
                goal=algorithm_config.goal,
                sessions=sessions,
                total_estimated_duration_minutes=total_duration,
                rest_day=False,
                last_performance=last_performance,
                notes=self._generate_workout_notes(algorithm_config, workout_preferences)
            )
            
            # 11. Salvar no Firestore
            await self._save_workout_plan(workout_plan)
            
            logger.info("Plano de treino gerado com sucesso", 
                       user_id=user_id, total_duration=total_duration)
            
            return workout_plan
            
        except Exception as e:
            logger.error("Erro ao gerar plano de treino", 
                        user_id=user_id, error=str(e))
            raise
    
    def _create_full_body_split(self) -> List[WorkoutTemplate]:
        """Cria split de corpo inteiro (1 dia)"""
        return [
            WorkoutTemplate(
                name="Full Body",
                muscle_groups_focus=[
                    MuscleGroup.PEITO, MuscleGroup.COSTAS, MuscleGroup.QUADRICEPS,
                    MuscleGroup.OMBROS, MuscleGroup.CORE
                ],
                workout_type=WorkoutType.STRENGTH,
                target_duration_minutes=60,
                exercise_slots=[
                    {"type": "compound", "muscle_groups": ["peito", "ombros", "triceps"], "sets": 3},
                    {"type": "compound", "muscle_groups": ["costas", "biceps"], "sets": 3},
                    {"type": "compound", "muscle_groups": ["quadriceps", "gluteos"], "sets": 3},
                    {"type": "compound", "muscle_groups": ["posterior", "gluteos"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["ombros"], "sets": 2},
                    {"type": "isolation", "muscle_groups": ["core"], "sets": 2}
                ],
                warmup_type="full_body",
                intensity_level=0.7
            )
        ]
    
    def _create_upper_lower_split(self) -> List[WorkoutTemplate]:
        """Cria split superior/inferior (2 dias)"""
        return [
            WorkoutTemplate(
                name="Upper Body",
                muscle_groups_focus=[
                    MuscleGroup.PEITO, MuscleGroup.COSTAS, MuscleGroup.OMBROS,
                    MuscleGroup.BICEPS, MuscleGroup.TRICEPS
                ],
                workout_type=WorkoutType.STRENGTH,
                target_duration_minutes=60,
                exercise_slots=[
                    {"type": "compound", "muscle_groups": ["peito", "ombros", "triceps"], "sets": 4},
                    {"type": "compound", "muscle_groups": ["costas", "biceps"], "sets": 4},
                    {"type": "isolation", "muscle_groups": ["ombros"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["biceps"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["triceps"], "sets": 3}
                ],
                warmup_type="upper_body",
                intensity_level=0.8
            ),
            WorkoutTemplate(
                name="Lower Body",
                muscle_groups_focus=[
                    MuscleGroup.QUADRICEPS, MuscleGroup.POSTERIOR, MuscleGroup.GLUTEOS,
                    MuscleGroup.PANTURRILHAS, MuscleGroup.CORE
                ],
                workout_type=WorkoutType.STRENGTH,
                target_duration_minutes=60,
                exercise_slots=[
                    {"type": "compound", "muscle_groups": ["quadriceps", "gluteos"], "sets": 4},
                    {"type": "compound", "muscle_groups": ["posterior", "gluteos"], "sets": 4},
                    {"type": "isolation", "muscle_groups": ["quadriceps"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["posterior"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["panturrilhas"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["core"], "sets": 3}
                ],
                warmup_type="lower_body",
                intensity_level=0.8
            )
        ]
    
    def _create_push_pull_legs_split(self) -> List[WorkoutTemplate]:
        """Cria split push/pull/legs (3 dias)"""
        return [
            WorkoutTemplate(
                name="Push (Empurrar)",
                muscle_groups_focus=[
                    MuscleGroup.PEITO, MuscleGroup.OMBROS, MuscleGroup.TRICEPS
                ],
                workout_type=WorkoutType.STRENGTH,
                target_duration_minutes=60,
                exercise_slots=[
                    {"type": "compound", "muscle_groups": ["peito", "ombros", "triceps"], "sets": 4},
                    {"type": "compound", "muscle_groups": ["ombros", "triceps"], "sets": 4},
                    {"type": "isolation", "muscle_groups": ["peito"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["ombros"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["triceps"], "sets": 3}
                ],
                warmup_type="upper_body",
                intensity_level=0.85
            ),
            WorkoutTemplate(
                name="Pull (Puxar)",
                muscle_groups_focus=[
                    MuscleGroup.COSTAS, MuscleGroup.BICEPS, MuscleGroup.ANTEBRACOS
                ],
                workout_type=WorkoutType.STRENGTH,
                target_duration_minutes=60,
                exercise_slots=[
                    {"type": "compound", "muscle_groups": ["costas", "biceps"], "sets": 4},
                    {"type": "compound", "muscle_groups": ["costas", "biceps"], "sets": 4},
                    {"type": "isolation", "muscle_groups": ["costas"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["biceps"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["antebracos"], "sets": 2}
                ],
                warmup_type="upper_body",
                intensity_level=0.85
            ),
            WorkoutTemplate(
                name="Legs (Pernas)",
                muscle_groups_focus=[
                    MuscleGroup.QUADRICEPS, MuscleGroup.POSTERIOR, MuscleGroup.GLUTEOS,
                    MuscleGroup.PANTURRILHAS, MuscleGroup.CORE
                ],
                workout_type=WorkoutType.STRENGTH,
                target_duration_minutes=70,
                exercise_slots=[
                    {"type": "compound", "muscle_groups": ["quadriceps", "gluteos"], "sets": 4},
                    {"type": "compound", "muscle_groups": ["posterior", "gluteos"], "sets": 4},
                    {"type": "isolation", "muscle_groups": ["quadriceps"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["posterior"], "sets": 3},
                    {"type": "isolation", "muscle_groups": ["panturrilhas"], "sets": 4},
                    {"type": "isolation", "muscle_groups": ["core"], "sets": 3}
                ],
                warmup_type="lower_body",
                intensity_level=0.85
            )
        ]
    
    def _create_upper_lower_push_pull_split(self) -> List[WorkoutTemplate]:
        """Cria split upper/lower/push/pull (4 dias)"""
        upper_lower = self._create_upper_lower_split()
        push_pull = self._create_push_pull_legs_split()[:2]  # Apenas push e pull
        return upper_lower + push_pull
    
    def _create_push_pull_legs_upper_lower_split(self) -> List[WorkoutTemplate]:
        """Cria split push/pull/legs/upper/lower (5 dias)"""
        ppl = self._create_push_pull_legs_split()
        upper_lower = self._create_upper_lower_split()
        return ppl + upper_lower
    
    def _create_push_pull_legs_x2_split(self) -> List[WorkoutTemplate]:
        """Cria split push/pull/legs repetido (6 dias)"""
        ppl = self._create_push_pull_legs_split()
        return ppl + ppl  # Repetir o ciclo
    
    def _create_daily_specialization_split(self) -> List[WorkoutTemplate]:
        """Cria split de especialização diária (7 dias)"""
        return [
            WorkoutTemplate(
                name="Peito Especialização",
                muscle_groups_focus=[MuscleGroup.PEITO, MuscleGroup.TRICEPS],
                workout_type=WorkoutType.STRENGTH,
                target_duration_minutes=60,
                exercise_slots=[
                    {"type": "compound", "muscle_groups": ["peito", "triceps"], "sets": 5},
                    {"type": "isolation", "muscle_groups": ["peito"], "sets": 4},
                    {"type": "isolation", "muscle_groups": ["peito"], "sets": 4},
                    {"type": "isolation", "muscle_groups": ["triceps"], "sets": 3}
                ],
                warmup_type="upper_body",
                intensity_level=0.9
            ),
            WorkoutTemplate(
                name="Costas Especialização",
                muscle_groups_focus=[MuscleGroup.COSTAS, MuscleGroup.BICEPS],
                workout_type=WorkoutType.STRENGTH,
                target_duration_minutes=60,
                exercise_slots=[
                    {"type": "compound", "muscle_groups": ["costas", "biceps"], "sets": 5},
                    {"type": "isolation", "muscle_groups": ["costas"], "sets": 4},
                    {"type": "isolation", "muscle_groups": ["costas"], "sets": 4},
                    {"type": "isolation", "muscle_groups": ["biceps"], "sets": 3}
                ],
                warmup_type="upper_body",
                intensity_level=0.9
            ),
            # Adicionar mais especializações...
        ]
    
    def _is_rest_day(self, target_date: date, preferences: WorkoutPreferences) -> bool:
        """Determina se é dia de descanso"""
        day_name = target_date.strftime("%A").lower()
        available_days = [day.lower() for day in preferences.available_days]
        
        return day_name not in available_days
    
    async def _create_rest_day_plan(
        self, 
        user_id: str, 
        target_date: date, 
        config: AlgorithmConfig
    ) -> WorkoutPlan:
        """Cria plano para dia de descanso"""
        
        # Determinar tipo de recuperação ativa baseado no objetivo
        active_recovery = None
        if config.goal == GoalType.PERDER_PESO:
            active_recovery = "Caminhada leve de 20-30 minutos"
        elif config.goal == GoalType.MELHORAR_RESISTENCIA:
            active_recovery = "Alongamento dinâmico e mobilidade"
        else:
            active_recovery = "Descanso completo ou alongamento suave"
        
        return WorkoutPlan(
            user_id=user_id,
            date=target_date,
            goal=config.goal,
            sessions=[],
            total_estimated_duration_minutes=0,
            rest_day=True,
            active_recovery=active_recovery,
            notes="Dia de descanso para recuperação muscular. A recuperação é essencial para o progresso!"
        )
    
    def _select_template_for_day(
        self, 
        day_of_week: str, 
        templates: List[WorkoutTemplate],
        preferences: WorkoutPreferences
    ) -> Optional[WorkoutTemplate]:
        """Seleciona template apropriado para o dia da semana"""
        if not templates:
            return None
        
        # Mapear dias da semana para índices de template
        day_mapping = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }
        
        template_index = day_mapping.get(day_of_week, 0) % len(templates)
        return templates[template_index]
    
    async def _get_available_exercises(self, preferences: WorkoutPreferences) -> List[ExerciseCandidate]:
        """Obtém exercícios disponíveis do Content Service"""
        try:
            # Buscar exercícios
            exercises_response = await self.content_service.get_exercises()
            exercises = exercises_response.get("exercises", [])
            
            candidates = []
            for exercise in exercises:
                # Filtrar por local e equipamento
                if self._exercise_matches_preferences(exercise, preferences):
                    candidate = ExerciseCandidate(
                        exercise_id=exercise["id"],
                        name=exercise["name"],
                        muscle_groups=exercise["muscle_groups"],
                        primary_muscle=exercise["muscle_groups"][0] if exercise["muscle_groups"] else "",
                        secondary_muscles=exercise["muscle_groups"][1:] if len(exercise["muscle_groups"]) > 1 else [],
                        equipment=exercise.get("equipment", "bodyweight"),
                        difficulty=DifficultyLevel(exercise.get("difficulty", "intermediate")),
                        movement_pattern=exercise.get("movement_pattern", "compound"),
                        safety_rating=exercise.get("safety_rating", 0.8),
                        effectiveness_rating=exercise.get("effectiveness_rating", 0.7),
                        location_compatibility=exercise.get("location_compatibility", ["gym"]),
                        time_efficiency=exercise.get("time_efficiency", 0.7)
                    )
                    candidates.append(candidate)
            
            # Ordenar por efetividade e segurança
            candidates.sort(key=lambda x: (x.effectiveness_rating * x.safety_rating), reverse=True)
            
            logger.info("Exercícios disponíveis obtidos", count=len(candidates))
            return candidates
            
        except Exception as e:
            logger.error("Erro ao obter exercícios", error=str(e))
            raise
    
    def _exercise_matches_preferences(self, exercise: dict, preferences: WorkoutPreferences) -> bool:
        """Verifica se o exercício atende às preferências"""
        # Verificar local
        exercise_locations = exercise.get("location_compatibility", ["gym"])
        if preferences.location not in exercise_locations:
            return False
        
        # Verificar equipamento disponível
        required_equipment = exercise.get("equipment", "bodyweight")
        if required_equipment != "bodyweight" and required_equipment not in preferences.equipment_available:
            return False
        
        return True
    
    async def _generate_workout_session(
        self,
        template: WorkoutTemplate,
        available_exercises: List[ExerciseCandidate],
        config: AlgorithmConfig,
        user_data: dict
    ) -> WorkoutSession:
        """Gera uma sessão de treino baseada no template"""
        
        # Gerar aquecimento
        warmup = self._generate_warmup(template.warmup_type)
        
        # Selecionar exercícios para cada slot
        exercises = []
        used_exercises = set()
        
        for slot in template.exercise_slots:
            exercise = self._select_exercise_for_slot(
                slot, available_exercises, used_exercises, config
            )
            if exercise:
                exercises.append(exercise)
                used_exercises.add(exercise.exercise_id)
        
        # Calcular duração estimada
        estimated_duration = self._calculate_session_duration(exercises, warmup)
        
        return WorkoutSession(
            session_id=f"{config.user_id}_{template.name}_{datetime.utcnow().strftime('%Y%m%d')}",
            name=template.name,
            workout_type=template.workout_type,
            muscle_groups_focus=template.muscle_groups_focus,
            difficulty=config.experience_level,
            estimated_duration_minutes=estimated_duration,
            warmup=warmup,
            exercises=exercises,
            cooldown_notes=self._generate_cooldown_notes(template),
            equipment_needed=list(set(ex.equipment for ex in exercises if hasattr(ex, 'equipment'))),
            location=config.workout_preferences.location,
            notes=self._generate_session_notes(template, config)
        )
    
    def _select_exercise_for_slot(
        self,
        slot: Dict,
        available_exercises: List[ExerciseCandidate],
        used_exercises: Set[str],
        config: AlgorithmConfig
    ) -> Optional[Exercise]:
        """Seleciona exercício apropriado para um slot específico"""
        
        # Filtrar exercícios candidatos
        candidates = []
        for exercise in available_exercises:
            if exercise.exercise_id in used_exercises:
                continue
            
            # Verificar tipo de movimento
            if slot["type"] != "any" and exercise.movement_pattern != slot["type"]:
                continue
            
            # Verificar grupos musculares
            slot_muscles = slot["muscle_groups"]
            if not any(muscle in exercise.muscle_groups for muscle in slot_muscles):
                continue
            
            # Verificar dificuldade
            if not self._is_appropriate_difficulty(exercise.difficulty, config.experience_level):
                continue
            
            candidates.append(exercise)
        
        if not candidates:
            return None
        
        # Selecionar melhor candidato
        selected_candidate = max(candidates, key=lambda x: x.effectiveness_rating * x.safety_rating)
        
        # Gerar sets para o exercício
        sets = self._generate_exercise_sets(selected_candidate, slot, config)
        
        return Exercise(
            exercise_id=selected_candidate.exercise_id,
            name=selected_candidate.name,
            muscle_groups=selected_candidate.muscle_groups,
            equipment=selected_candidate.equipment,
            difficulty=selected_candidate.difficulty,
            sets=sets,
            instructions=f"Execute {len(sets)} séries deste exercício",
            tips=self._generate_exercise_tips(selected_candidate, config),
            safety_notes=self._generate_safety_notes(selected_candidate)
        )
    
    def _generate_exercise_sets(
        self,
        exercise: ExerciseCandidate,
        slot: Dict,
        config: AlgorithmConfig
    ) -> List[ExerciseSet]:
        """Gera séries para um exercício"""
        
        num_sets = slot.get("sets", 3)
        volume_config = self.workout_config["volume_config"][config.experience_level.value]
        intensity_config = self.workout_config["intensity_config"][config.goal.value]
        
        # Determinar range de repetições baseado no objetivo
        if config.goal == GoalType.AUMENTAR_FORCA:
            rep_range = volume_config["reps_range"]["strength"]
        elif config.goal == GoalType.MELHORAR_RESISTENCIA:
            rep_range = volume_config["reps_range"]["endurance"]
        else:
            rep_range = volume_config["reps_range"]["hypertrophy"]
        
        # Determinar descanso entre séries
        rest_range = intensity_config["rest_between_sets"]
        rest_seconds = random.randint(rest_range["min"], rest_range["max"])
        
        sets = []
        for i in range(num_sets):
            # Variar repetições dentro do range
            reps = random.randint(rep_range[0], rep_range[1])
            
            # Ajustar peso baseado na série (pirâmide)
            weight_factor = 1.0 - (i * 0.05)  # Reduzir 5% a cada série
            
            exercise_set = ExerciseSet(
                set_number=i + 1,
                reps=reps,
                weight=None,  # Será definido pelo usuário
                rest_seconds=rest_seconds,
                notes=f"Série {i + 1} - Foque na técnica"
            )
            sets.append(exercise_set)
        
        return sets
    
    def _generate_warmup(self, warmup_type: str) -> Warmup:
        """Gera aquecimento baseado no tipo"""
        warmup_config = self.workout_config["warmup_config"].get(warmup_type, 
                                                                self.workout_config["warmup_config"]["full_body"])
        
        exercises = []
        for exercise_name in warmup_config["exercises"]:
            warmup_exercise = WarmupExercise(
                name=exercise_name.replace("_", " ").title(),
                duration_seconds=120,  # 2 minutos por exercício
                instructions=f"Execute {exercise_name.replace('_', ' ')} por 2 minutos"
            )
            exercises.append(warmup_exercise)
        
        return Warmup(
            total_duration_minutes=warmup_config["duration_minutes"],
            exercises=exercises,
            notes="Aquecimento é essencial para prevenir lesões e melhorar performance"
        )
    
    def _is_appropriate_difficulty(self, exercise_difficulty: DifficultyLevel, user_level: DifficultyLevel) -> bool:
        """Verifica se a dificuldade do exercício é apropriada"""
        difficulty_order = {
            DifficultyLevel.BEGINNER: 0,
            DifficultyLevel.INTERMEDIATE: 1,
            DifficultyLevel.ADVANCED: 2,
            DifficultyLevel.EXPERT: 3
        }
        
        exercise_level = difficulty_order[exercise_difficulty]
        user_level_num = difficulty_order[user_level]
        
        # Permitir exercícios até 1 nível acima do usuário
        return exercise_level <= user_level_num + 1
    
    def _calculate_session_duration(self, exercises: List[Exercise], warmup: Warmup) -> int:
        """Calcula duração estimada da sessão"""
        warmup_duration = warmup.total_duration_minutes if warmup else 0
        
        exercise_duration = 0
        for exercise in exercises:
            # Estimar tempo por série (2-3 minutos incluindo descanso)
            sets_duration = len(exercise.sets) * 2.5
            exercise_duration += sets_duration
        
        # Adicionar tempo de cooldown
        cooldown_duration = 5
        
        return int(warmup_duration + exercise_duration + cooldown_duration)
    
    def _generate_exercise_tips(self, exercise: ExerciseCandidate, config: AlgorithmConfig) -> List[str]:
        """Gera dicas específicas para o exercício"""
        tips = []
        
        if exercise.movement_pattern == "compound":
            tips.append("Exercício composto - trabalha múltiplos grupos musculares")
        
        if exercise.difficulty == DifficultyLevel.ADVANCED:
            tips.append("Exercício avançado - foque na técnica perfeita")
        
        if config.goal == GoalType.PERDER_PESO:
            tips.append("Mantenha intensidade alta para maximizar queima calórica")
        elif config.goal == GoalType.GANHAR_MASSA:
            tips.append("Foque na conexão mente-músculo para máximo estímulo")
        
        return tips[:2]  # Máximo 2 dicas
    
    def _generate_safety_notes(self, exercise: ExerciseCandidate) -> List[str]:
        """Gera notas de segurança para o exercício"""
        safety_notes = []
        
        if exercise.safety_rating < 0.7:
            safety_notes.append("Exercício requer atenção especial à técnica")
        
        if "spine" in exercise.name.lower() or "back" in exercise.name.lower():
            safety_notes.append("Mantenha coluna neutra durante todo o movimento")
        
        if exercise.equipment in ["barbell", "dumbbell"]:
            safety_notes.append("Use sempre um spotter quando necessário")
        
        return safety_notes
    
    def _generate_cooldown_notes(self, template: WorkoutTemplate) -> str:
        """Gera notas de cooldown para a sessão"""
        cooldown_notes = {
            "upper_body": "Alongue peito, ombros e braços. Mantenha cada posição por 30 segundos.",
            "lower_body": "Alongue quadríceps, posteriores e panturrilhas. Foque na flexibilidade.",
            "full_body": "Alongamento geral de 5-10 minutos. Respire profundamente e relaxe."
        }
        
        return cooldown_notes.get(template.warmup_type, cooldown_notes["full_body"])
    
    def _generate_session_notes(self, template: WorkoutTemplate, config: AlgorithmConfig) -> str:
        """Gera notas específicas para a sessão"""
        notes = []
        
        if config.goal == GoalType.PERDER_PESO:
            notes.append("Mantenha intensidade alta e descansos curtos.")
        elif config.goal == GoalType.GANHAR_MASSA:
            notes.append("Foque na sobrecarga progressiva e técnica perfeita.")
        elif config.goal == GoalType.AUMENTAR_FORCA:
            notes.append("Priorize cargas altas com descansos adequados.")
        
        notes.append(f"Treino focado em: {', '.join(template.muscle_groups_focus)}")
        
        return " ".join(notes)
    
    def _generate_workout_notes(self, config: AlgorithmConfig, preferences: WorkoutPreferences) -> str:
        """Gera notas gerais para o plano de treino"""
        notes = []
        
        notes.append(f"Plano personalizado para {config.goal.value.replace('_', ' ')}.")
        notes.append(f"Nível: {config.experience_level.value}")
        notes.append(f"Local: {preferences.location}")
        
        return " ".join(notes)
    
    # Métodos auxiliares (similares ao diet_generator)
    
    async def _get_existing_plan(self, user_id: str, target_date: date) -> Optional[WorkoutPlan]:
        """Busca plano existente no Firestore"""
        try:
            doc_ref = self.firebase_service.db.collection("workout_plans").document(f"{user_id}_{target_date}")
            doc = await doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return WorkoutPlan(**data)
            
            return None
        except Exception as e:
            logger.error("Erro ao buscar plano de treino existente", error=str(e))
            return None
    
    def _should_regenerate_plan(self, existing_plan: WorkoutPlan, config: AlgorithmConfig) -> bool:
        """Verifica se deve regenerar um plano existente"""
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
    
    async def _get_last_performance(self, user_id: str, workout_name: str) -> Optional[Dict]:
        """Obtém dados de performance da última sessão similar"""
        try:
            # Buscar últimas performances do usuário
            query = (self.firebase_service.db.collection("workout_performances")
                    .where("user_id", "==", user_id)
                    .where("workout_name", "==", workout_name)
                    .order_by("date", direction="desc")
                    .limit(1))
            
            docs = await query.get()
            
            if docs:
                return docs[0].to_dict()
            
            return None
        except Exception as e:
            logger.error("Erro ao obter performance anterior", error=str(e))
            return None
    
    async def _save_workout_plan(self, workout_plan: WorkoutPlan):
        """Salva o plano de treino no Firestore"""
        try:
            doc_id = f"{workout_plan.user_id}_{workout_plan.date}"
            doc_ref = self.firebase_service.db.collection("workout_plans").document(doc_id)
            
            # Converter para dict
            plan_data = workout_plan.dict()
            plan_data["created_at"] = datetime.utcnow()
            plan_data["updated_at"] = datetime.utcnow()
            
            await doc_ref.set(plan_data)
            
            logger.info("Plano de treino salvo", user_id=workout_plan.user_id, date=workout_plan.date)
            
        except Exception as e:
            logger.error("Erro ao salvar plano de treino", error=str(e))
            raise


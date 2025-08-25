"""
Rotas para dashboard e agregação de dados
"""

import asyncio
from datetime import datetime, date
from typing import Dict, Any, Optional
import structlog

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import JSONResponse

from models.tracking import DashboardResponse, NutritionalSummary, WorkoutSummary, EnergyBalance, ProgressMetric
from services.firebase_service import FirebaseService
from services.service_client import ServiceClient
from services.calorie_service import CalorieService
from services.cache_service import CacheService
from middleware.auth import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()


def get_firebase_service(request: Request) -> FirebaseService:
    """Dependency para obter serviço Firebase"""
    return request.app.state.firebase


def get_service_client(request: Request) -> ServiceClient:
    """Dependency para obter cliente de serviços"""
    if not hasattr(request.app.state, 'service_client'):
        request.app.state.service_client = ServiceClient()
    return request.app.state.service_client


def get_calorie_service(request: Request) -> CalorieService:
    """Dependency para obter serviço de cálculo calórico"""
    if not hasattr(request.app.state, 'calorie_service'):
        request.app.state.calorie_service = CalorieService(
            firebase_service=request.app.state.firebase
        )
    return request.app.state.calorie_service


def get_cache_service(request: Request) -> CacheService:
    """Dependency para obter serviço de cache"""
    return request.app.state.cache


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    target_date: Optional[str] = Query(None, description="Data no formato YYYY-MM-DD (padrão: hoje)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
    service_client: ServiceClient = Depends(get_service_client),
    calorie_service: CalorieService = Depends(get_calorie_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """
    Endpoint orquestrador do dashboard principal
    
    Este endpoint consolida dados de múltiplos serviços para alimentar
    a tela "Hoje" do aplicativo, incluindo:
    - Metas nutricionais vs. consumo atual
    - Plano de treino vs. execução
    - Balanço energético dinâmico
    - Métricas de progresso
    """
    try:
        user_id = current_user["user_id"]
        
        # Determinar data alvo
        if target_date:
            try:
                dashboard_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Formato de data inválido. Use YYYY-MM-DD"
                )
        else:
            dashboard_date = date.today()
        
        date_str = dashboard_date.isoformat()
        
        logger.info("Iniciando geração de dashboard", 
                   user_id=user_id,
                   date=date_str)
        
        # Verificar cache primeiro
        cached_dashboard = await cache_service.get_dashboard_cache(user_id, date_str)
        if cached_dashboard:
            logger.info("Dashboard obtido do cache", user_id=user_id, date=date_str)
            return DashboardResponse(**cached_dashboard)
        
        # Executar chamadas em paralelo para otimizar performance
        tasks = [
            # 1. Obter perfil do usuário (nickname, BMR, TDEE)
            service_client.get_user_profile(user_id),
            
            # 2. Obter metas diárias (calorias, macros)
            service_client.get_daily_targets(user_id, date_str),
            
            # 3. Obter plano de treino do dia
            service_client.get_workout_plan(user_id, date_str),
            
            # 4. Obter plano de refeições do dia
            service_client.get_meal_plan(user_id, date_str),
            
            # 5. Obter logs do dia atual
            firebase_service.get_daily_logs(user_id, dashboard_date)
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            user_profile, daily_targets, workout_plan, meal_plan, daily_logs = results
            
            # Tratar exceções individuais
            if isinstance(user_profile, Exception):
                logger.warning("Erro ao obter perfil do usuário", error=str(user_profile))
                user_profile = {"nickname": "Usuário", "weight_kg": 70, "bmr": 1800, "tdee": 2200}
            
            if isinstance(daily_targets, Exception):
                logger.warning("Erro ao obter metas diárias", error=str(daily_targets))
                daily_targets = {"calories": 2000, "protein": 150, "carbs": 200, "fat": 67, "water_ml": 2500}
            
            if isinstance(workout_plan, Exception):
                logger.warning("Erro ao obter plano de treino", error=str(workout_plan))
                workout_plan = {}
            
            if isinstance(meal_plan, Exception):
                logger.warning("Erro ao obter plano de refeições", error=str(meal_plan))
                meal_plan = {}
            
            if isinstance(daily_logs, Exception):
                logger.warning("Erro ao obter logs diários", error=str(daily_logs))
                daily_logs = []
                
        except Exception as e:
            logger.error("Erro nas chamadas paralelas", error=str(e))
            raise HTTPException(
                status_code=500,
                detail="Erro ao obter dados dos serviços"
            )
        
        # Processar dados obtidos
        
        # 1. Resumo nutricional
        nutritional_summary = await _build_nutritional_summary(
            daily_logs, daily_targets, meal_plan
        )
        
        # 2. Resumo de treino
        workout_summary = await _build_workout_summary(
            daily_logs, workout_plan
        )
        
        # 3. Balanço energético
        energy_balance = await calorie_service.calculate_daily_energy_balance(
            user_id=user_id,
            target_date=dashboard_date,
            user_bmr=user_profile.get("bmr", 1800),
            user_tdee=user_profile.get("tdee", 2200),
            daily_logs=daily_logs
        )
        
        # 4. Métricas de progresso (últimas medições)
        progress_highlights = await _build_progress_highlights(
            firebase_service, user_id
        )
        
        # 5. Calcular streak
        daily_streak = await firebase_service.get_user_streak(user_id)
        
        # 6. Gerar mensagem motivacional
        motivation_message = _generate_motivation_message(
            nutritional_summary, workout_summary, daily_streak
        )
        
        # 7. Próximo marco
        next_milestone = _get_next_milestone(
            nutritional_summary, workout_summary, progress_highlights
        )
        
        # Construir resposta do dashboard
        dashboard_response = DashboardResponse(
            user_id=user_id,
            user_name=user_profile.get("nickname", "Usuário"),
            date=dashboard_date,
            nutritional_summary=nutritional_summary,
            workout_summary=workout_summary,
            energy_balance=EnergyBalance(**energy_balance),
            progress_highlights=progress_highlights,
            daily_streak=daily_streak,
            motivation_message=motivation_message,
            next_milestone=next_milestone
        )
        
        # Salvar no cache
        await cache_service.set_dashboard_cache(
            user_id, date_str, dashboard_response.dict()
        )
        
        logger.info("Dashboard gerado com sucesso", 
                   user_id=user_id,
                   date=date_str,
                   calories_consumed=nutritional_summary.calories_consumed,
                   workout_completed=workout_summary.workout_completed)
        
        return dashboard_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao gerar dashboard", 
                    user_id=current_user.get("user_id"),
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao gerar dashboard"
        )


async def _build_nutritional_summary(
    daily_logs: list,
    daily_targets: dict,
    meal_plan: dict
) -> NutritionalSummary:
    """Constrói resumo nutricional do dia"""
    
    # Inicializar contadores
    calories_consumed = 0.0
    protein_consumed = 0.0
    carbs_consumed = 0.0
    fat_consumed = 0.0
    water_consumed_ml = 0.0
    meals_completed = 0
    
    # Processar logs de refeições
    meal_types_completed = set()
    
    for log in daily_logs:
        if log.get("log_type") == "meal_checkin":
            nutritional = log.get("value", {}).get("nutritional_summary", {})
            calories_consumed += nutritional.get("total_calories", 0)
            protein_consumed += nutritional.get("total_protein", 0)
            carbs_consumed += nutritional.get("total_carbs", 0)
            fat_consumed += nutritional.get("total_fat", 0)
            
            # Contar refeição como completa
            meal_type = log.get("value", {}).get("meal_type")
            if meal_type:
                meal_types_completed.add(meal_type)
        
        elif log.get("log_type") == "water_intake":
            water_consumed_ml += log.get("value", {}).get("amount_ml", 0)
    
    meals_completed = len(meal_types_completed)
    
    # Obter metas
    calories_target = daily_targets.get("calories", 2000)
    protein_target = daily_targets.get("protein", 150)
    carbs_target = daily_targets.get("carbs", 200)
    fat_target = daily_targets.get("fat", 67)
    water_target_ml = daily_targets.get("water_ml", 2500)
    
    # Calcular refeições planejadas
    total_meals = len(meal_plan.get("meals", [])) if meal_plan else 6  # Padrão 6 refeições
    
    return NutritionalSummary(
        calories_consumed=round(calories_consumed, 1),
        calories_target=round(calories_target, 1),
        calories_remaining=round(max(0, calories_target - calories_consumed), 1),
        protein_consumed=round(protein_consumed, 1),
        protein_target=round(protein_target, 1),
        carbs_consumed=round(carbs_consumed, 1),
        carbs_target=round(carbs_target, 1),
        fat_consumed=round(fat_consumed, 1),
        fat_target=round(fat_target, 1),
        water_consumed_ml=round(water_consumed_ml, 1),
        water_target_ml=round(water_target_ml, 1),
        meals_completed=meals_completed,
        total_meals=total_meals
    )


async def _build_workout_summary(
    daily_logs: list,
    workout_plan: dict
) -> WorkoutSummary:
    """Constrói resumo de treino do dia"""
    
    # Verificar se há treino planejado
    workout_planned = bool(workout_plan.get("exercises"))
    workout_name = workout_plan.get("name", "Treino do Dia")
    duration_planned_minutes = workout_plan.get("estimated_duration_minutes", 60)
    planned_exercises = workout_plan.get("exercises", [])
    muscle_groups_focus = workout_plan.get("muscle_groups", [])
    
    # Processar logs de treino
    workout_completed = False
    duration_actual_minutes = 0
    calories_burned = 0.0
    exercises_completed = 0
    completed_exercise_ids = set()
    
    for log in daily_logs:
        if log.get("log_type") == "workout_session":
            workout_completed = True
            duration_actual_minutes += log.get("value", {}).get("duration_minutes", 0)
            calories_burned += log.get("value", {}).get("calories_burned", 0)
            
            # Contar exercícios únicos realizados
            exercises_performed = log.get("value", {}).get("exercises_performed", [])
            completed_exercise_ids.update(exercises_performed)
        
        elif log.get("log_type") == "set":
            # Contar exercícios por séries realizadas
            exercise_id = log.get("value", {}).get("exercise_id")
            if exercise_id:
                completed_exercise_ids.add(exercise_id)
    
    exercises_completed = len(completed_exercise_ids)
    total_exercises = len(planned_exercises)
    
    return WorkoutSummary(
        workout_planned=workout_planned,
        workout_completed=workout_completed,
        workout_name=workout_name,
        duration_planned_minutes=duration_planned_minutes,
        duration_actual_minutes=duration_actual_minutes,
        calories_burned=round(calories_burned, 1),
        exercises_completed=exercises_completed,
        total_exercises=total_exercises,
        muscle_groups_focus=muscle_groups_focus
    )


async def _build_progress_highlights(
    firebase_service: FirebaseService,
    user_id: str
) -> list:
    """Constrói destaques de progresso"""
    
    progress_highlights = []
    
    try:
        # Obter últimas medições de peso
        weight_history = await firebase_service.get_weight_history(user_id, days=7)
        if len(weight_history) >= 2:
            latest_weight = weight_history[-1]["weight_kg"]
            previous_weight = weight_history[-2]["weight_kg"]
            weight_change = latest_weight - previous_weight
            
            progress_highlights.append(ProgressMetric(
                metric_name="Peso Corporal",
                current_value=latest_weight,
                previous_value=previous_weight,
                change_value=weight_change,
                change_percentage=(weight_change / previous_weight * 100) if previous_weight > 0 else 0,
                trend="down" if weight_change < -0.1 else "up" if weight_change > 0.1 else "stable",
                unit="kg",
                last_updated=datetime.utcnow()
            ))
        
        # Obter progresso de força (exercício mais recente)
        strength_progress = await firebase_service.get_strength_progress(user_id, days=30)
        if strength_progress:
            # Agrupar por exercício e pegar o mais recente
            exercise_progress = {}
            for entry in strength_progress:
                exercise_id = entry["exercise_id"]
                if exercise_id not in exercise_progress:
                    exercise_progress[exercise_id] = []
                exercise_progress[exercise_id].append(entry)
            
            # Pegar exercício com mais progresso recente
            for exercise_id, entries in exercise_progress.items():
                if len(entries) >= 2:
                    entries.sort(key=lambda x: x["date"])
                    latest = entries[-1]
                    previous = entries[-2]
                    
                    weight_change = latest["weight_kg"] - previous["weight_kg"]
                    if abs(weight_change) > 0.5:  # Mudança significativa
                        progress_highlights.append(ProgressMetric(
                            metric_name=f"Força - {latest['exercise_name']}",
                            current_value=latest["weight_kg"],
                            previous_value=previous["weight_kg"],
                            change_value=weight_change,
                            change_percentage=(weight_change / previous["weight_kg"] * 100) if previous["weight_kg"] > 0 else 0,
                            trend="up" if weight_change > 0 else "down",
                            unit="kg",
                            last_updated=datetime.utcnow()
                        ))
                        break  # Apenas um destaque de força
        
    except Exception as e:
        logger.error("Erro ao construir destaques de progresso", error=str(e))
    
    return progress_highlights


def _generate_motivation_message(
    nutritional_summary: NutritionalSummary,
    workout_summary: WorkoutSummary,
    daily_streak: int
) -> str:
    """Gera mensagem motivacional personalizada"""
    
    messages = []
    
    # Mensagens baseadas em streak
    if daily_streak >= 7:
        messages.append(f"🔥 Incrível! {daily_streak} dias consecutivos seguindo seu plano!")
    elif daily_streak >= 3:
        messages.append(f"💪 Ótimo! {daily_streak} dias de consistência!")
    elif daily_streak >= 1:
        messages.append("🌟 Continue assim! Consistência é a chave do sucesso!")
    else:
        messages.append("🚀 Hoje é um novo dia para alcançar seus objetivos!")
    
    # Mensagens baseadas no progresso nutricional
    calories_percentage = (nutritional_summary.calories_consumed / nutritional_summary.calories_target * 100) if nutritional_summary.calories_target > 0 else 0
    
    if calories_percentage >= 90:
        messages.append("🎯 Meta calórica quase atingida!")
    elif calories_percentage >= 70:
        messages.append("📈 Bom progresso nas calorias hoje!")
    elif calories_percentage < 50:
        messages.append("🍽️ Lembre-se de se alimentar adequadamente!")
    
    # Mensagens baseadas no treino
    if workout_summary.workout_completed:
        messages.append("💪 Treino concluído! Excelente trabalho!")
    elif workout_summary.workout_planned:
        messages.append("🏋️ Seu treino está te esperando!")
    
    return " ".join(messages)


def _get_next_milestone(
    nutritional_summary: NutritionalSummary,
    workout_summary: WorkoutSummary,
    progress_highlights: list
) -> str:
    """Determina o próximo marco do usuário"""
    
    # Verificar próximo marco nutricional
    calories_percentage = (nutritional_summary.calories_consumed / nutritional_summary.calories_target * 100) if nutritional_summary.calories_target > 0 else 0
    
    if calories_percentage < 25:
        return "Próximo: Completar café da manhã"
    elif calories_percentage < 50:
        return "Próximo: Atingir 50% das calorias diárias"
    elif calories_percentage < 75:
        return "Próximo: Completar almoço"
    elif calories_percentage < 100:
        return "Próximo: Atingir meta calórica do dia"
    
    # Verificar próximo marco de treino
    if workout_summary.workout_planned and not workout_summary.workout_completed:
        return "Próximo: Completar treino do dia"
    elif workout_summary.exercises_completed < workout_summary.total_exercises:
        remaining = workout_summary.total_exercises - workout_summary.exercises_completed
        return f"Próximo: Completar {remaining} exercícios restantes"
    
    # Marco padrão
    return "Próximo: Manter consistência amanhã"


@router.get("/summary")
async def get_dashboard_summary(
    current_user: Dict[str, Any] = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service)
):
    """
    Obtém resumo rápido do dashboard (versão leve)
    
    Retorna apenas métricas essenciais para widgets ou notificações
    """
    try:
        user_id = current_user["user_id"]
        today = date.today()
        
        # Obter logs do dia
        daily_logs = await firebase_service.get_daily_logs(user_id, today)
        
        # Calcular métricas básicas
        calories_consumed = sum(
            log.get("value", {}).get("nutritional_summary", {}).get("total_calories", 0)
            for log in daily_logs
            if log.get("log_type") == "meal_checkin"
        )
        
        workout_completed = any(
            log.get("log_type") == "workout_session"
            for log in daily_logs
        )
        
        meals_completed = len(set(
            log.get("value", {}).get("meal_type")
            for log in daily_logs
            if log.get("log_type") == "meal_checkin" and log.get("value", {}).get("meal_type")
        ))
        
        return {
            "success": True,
            "data": {
                "date": today.isoformat(),
                "calories_consumed": round(calories_consumed, 1),
                "workout_completed": workout_completed,
                "meals_completed": meals_completed,
                "logs_count": len(daily_logs)
            }
        }
        
    except Exception as e:
        logger.error("Erro ao obter resumo do dashboard", 
                    user_id=current_user.get("user_id"),
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter resumo"
        )


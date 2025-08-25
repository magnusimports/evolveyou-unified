"""
Rotas para logging de atividades do usuário
"""

from datetime import datetime, date
from typing import Dict, Any
import structlog

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from models.tracking import (
    MealCheckinRequest, SetRequest, BodyWeightRequest, WorkoutSessionEndRequest,
    SuccessResponse, LogType, DailyLog
)
from services.firebase_service import FirebaseService
from services.calorie_service import CalorieService
from services.service_client import ServiceClient
from middleware.auth import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()


def get_firebase_service(request: Request) -> FirebaseService:
    """Dependency para obter serviço Firebase"""
    return request.app.state.firebase


def get_calorie_service(request: Request) -> CalorieService:
    """Dependency para obter serviço de cálculo calórico"""
    if not hasattr(request.app.state, 'calorie_service'):
        request.app.state.calorie_service = CalorieService(
            firebase_service=request.app.state.firebase
        )
    return request.app.state.calorie_service


def get_service_client(request: Request) -> ServiceClient:
    """Dependency para obter cliente de serviços"""
    if not hasattr(request.app.state, 'service_client'):
        request.app.state.service_client = ServiceClient()
    return request.app.state.service_client


@router.post("/meal-checkin", response_model=SuccessResponse)
async def log_meal_checkin(
    meal_data: MealCheckinRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service)
):
    """
    Registra o consumo de uma refeição completa
    
    Este endpoint permite que o usuário faça check-in de uma refeição,
    registrando todos os alimentos consumidos e seus valores nutricionais.
    """
    try:
        user_id = current_user["user_id"]
        
        logger.info("Iniciando log de refeição", 
                   user_id=user_id,
                   meal_type=meal_data.meal_type)
        
        # Validar dados da refeição
        if not meal_data.foods_consumed:
            raise HTTPException(
                status_code=400,
                detail="Lista de alimentos não pode estar vazia"
            )
        
        # Validar total de calorias
        if meal_data.total_calories <= 0:
            raise HTTPException(
                status_code=400,
                detail="Total de calorias deve ser maior que zero"
            )
        
        # Preparar dados do log
        log_data = DailyLog(
            user_id=user_id,
            log_type=LogType.MEAL_CHECKIN,
            timestamp=datetime.utcnow(),
            date=date.today(),
            value={
                "meal_type": meal_data.meal_type,
                "foods_consumed": meal_data.foods_consumed,
                "nutritional_summary": {
                    "total_calories": meal_data.total_calories,
                    "total_protein": meal_data.total_protein,
                    "total_carbs": meal_data.total_carbs,
                    "total_fat": meal_data.total_fat
                },
                "notes": meal_data.notes
            },
            metadata={
                "source": "mobile_app",
                "version": "1.0"
            }
        )
        
        # Salvar no Firestore
        log_id = await firebase_service.save_daily_log(log_data.dict())
        
        logger.info("Refeição registrada com sucesso", 
                   user_id=user_id,
                   log_id=log_id,
                   calories=meal_data.total_calories)
        
        return SuccessResponse(
            message="Refeição registrada com sucesso",
            data={
                "log_id": log_id,
                "meal_type": meal_data.meal_type,
                "calories": meal_data.total_calories
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao registrar refeição", 
                    user_id=current_user.get("user_id"),
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao registrar refeição"
        )


@router.post("/set", response_model=SuccessResponse)
async def log_set(
    set_data: SetRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service)
):
    """
    Registra uma série de treino realizada
    
    Este endpoint permite registrar cada série individual de um exercício,
    incluindo peso utilizado, repetições realizadas e percepção de esforço.
    """
    try:
        user_id = current_user["user_id"]
        
        logger.info("Iniciando log de série", 
                   user_id=user_id,
                   exercise_id=set_data.exercise_id,
                   set_number=set_data.set_number)
        
        # Validar dados da série
        if set_data.weight_kg is not None and set_data.weight_kg < 0:
            raise HTTPException(
                status_code=400,
                detail="Peso não pode ser negativo"
            )
        
        if set_data.reps_done <= 0:
            raise HTTPException(
                status_code=400,
                detail="Número de repetições deve ser maior que zero"
            )
        
        # Preparar dados do log
        log_data = DailyLog(
            user_id=user_id,
            log_type=LogType.SET,
            timestamp=datetime.utcnow(),
            date=date.today(),
            value={
                "exercise_id": set_data.exercise_id,
                "exercise_name": set_data.exercise_name,
                "weight_kg": set_data.weight_kg,
                "reps_done": set_data.reps_done,
                "set_number": set_data.set_number,
                "rpe": set_data.rpe,
                "notes": set_data.notes
            },
            metadata={
                "source": "mobile_app",
                "version": "1.0"
            }
        )
        
        # Salvar no Firestore
        log_id = await firebase_service.save_daily_log(log_data.dict())
        
        logger.info("Série registrada com sucesso", 
                   user_id=user_id,
                   log_id=log_id,
                   exercise=set_data.exercise_name,
                   weight=set_data.weight_kg,
                   reps=set_data.reps_done)
        
        return SuccessResponse(
            message="Série registrada com sucesso",
            data={
                "log_id": log_id,
                "exercise_name": set_data.exercise_name,
                "weight_kg": set_data.weight_kg,
                "reps_done": set_data.reps_done,
                "set_number": set_data.set_number
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao registrar série", 
                    user_id=current_user.get("user_id"),
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao registrar série"
        )


@router.post("/body-weight", response_model=SuccessResponse)
async def log_body_weight(
    weight_data: BodyWeightRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service)
):
    """
    Registra uma nova pesagem do usuário
    
    Este endpoint permite registrar o peso corporal e opcionalmente
    outras métricas como percentual de gordura e massa muscular.
    """
    try:
        user_id = current_user["user_id"]
        
        logger.info("Iniciando log de peso", 
                   user_id=user_id,
                   weight=weight_data.weight_kg)
        
        # Validar peso
        if weight_data.weight_kg < 30 or weight_data.weight_kg > 300:
            raise HTTPException(
                status_code=400,
                detail="Peso deve estar entre 30kg e 300kg"
            )
        
        # Validar percentual de gordura se fornecido
        if (weight_data.body_fat_percentage is not None and 
            (weight_data.body_fat_percentage < 0 or weight_data.body_fat_percentage > 50)):
            raise HTTPException(
                status_code=400,
                detail="Percentual de gordura deve estar entre 0% e 50%"
            )
        
        # Preparar dados do log
        log_data = DailyLog(
            user_id=user_id,
            log_type=LogType.BODY_WEIGHT,
            timestamp=datetime.utcnow(),
            date=date.today(),
            value={
                "weight_kg": weight_data.weight_kg,
                "body_fat_percentage": weight_data.body_fat_percentage,
                "muscle_mass_kg": weight_data.muscle_mass_kg,
                "notes": weight_data.notes
            },
            metadata={
                "source": "mobile_app",
                "version": "1.0"
            }
        )
        
        # Salvar no Firestore
        log_id = await firebase_service.save_daily_log(log_data.dict())
        
        logger.info("Peso registrado com sucesso", 
                   user_id=user_id,
                   log_id=log_id,
                   weight=weight_data.weight_kg)
        
        return SuccessResponse(
            message="Peso registrado com sucesso",
            data={
                "log_id": log_id,
                "weight_kg": weight_data.weight_kg,
                "body_fat_percentage": weight_data.body_fat_percentage,
                "muscle_mass_kg": weight_data.muscle_mass_kg
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao registrar peso", 
                    user_id=current_user.get("user_id"),
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao registrar peso"
        )


@router.post("/workout-session/end", response_model=SuccessResponse)
async def log_workout_session_end(
    session_data: WorkoutSessionEndRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
    calorie_service: CalorieService = Depends(get_calorie_service),
    service_client: ServiceClient = Depends(get_service_client)
):
    """
    Registra o fim de uma sessão de treino
    
    Este endpoint calcula o gasto calórico da sessão baseado nos exercícios
    realizados, duração e peso do usuário, consultando outros microserviços.
    """
    try:
        user_id = current_user["user_id"]
        
        logger.info("Iniciando log de fim de treino", 
                   user_id=user_id,
                   session_id=session_data.session_id,
                   duration=session_data.duration_minutes)
        
        # Validar duração
        if session_data.duration_minutes <= 0 or session_data.duration_minutes > 300:
            raise HTTPException(
                status_code=400,
                detail="Duração deve estar entre 1 e 300 minutos"
            )
        
        # Validar exercícios
        if not session_data.exercises_performed:
            raise HTTPException(
                status_code=400,
                detail="Lista de exercícios não pode estar vazia"
            )
        
        # Obter peso do usuário do Users Service
        try:
            user_profile = await service_client.get_user_profile(user_id)
            user_weight = user_profile.get("weight_kg", 70)  # Default 70kg
        except Exception as e:
            logger.warning("Erro ao obter peso do usuário, usando padrão", 
                          user_id=user_id, error=str(e))
            user_weight = 70
        
        # Obter valores MET dos exercícios do Content Service
        try:
            met_values = await service_client.get_exercise_met_values(
                session_data.exercises_performed
            )
        except Exception as e:
            logger.warning("Erro ao obter valores MET, usando padrão", 
                          exercises=session_data.exercises_performed, error=str(e))
            # Usar valor MET padrão para treino de força
            met_values = {ex_id: 6.0 for ex_id in session_data.exercises_performed}
        
        # Calcular gasto calórico da sessão
        calories_burned = await calorie_service.calculate_workout_calories(
            user_weight=user_weight,
            duration_minutes=session_data.duration_minutes,
            met_values=met_values,
            intensity_factor=session_data.perceived_intensity / 10.0 if session_data.perceived_intensity else 1.0
        )
        
        # Preparar dados do log
        log_data = DailyLog(
            user_id=user_id,
            log_type=LogType.WORKOUT_SESSION,
            timestamp=datetime.utcnow(),
            date=date.today(),
            value={
                "session_id": session_data.session_id,
                "duration_minutes": session_data.duration_minutes,
                "exercises_performed": session_data.exercises_performed,
                "perceived_intensity": session_data.perceived_intensity,
                "calories_burned": calories_burned,
                "user_weight_kg": user_weight,
                "met_values_used": met_values,
                "notes": session_data.notes
            },
            metadata={
                "source": "mobile_app",
                "version": "1.0",
                "calculation_method": "met_based"
            }
        )
        
        # Salvar no Firestore
        log_id = await firebase_service.save_daily_log(log_data.dict())
        
        logger.info("Sessão de treino registrada com sucesso", 
                   user_id=user_id,
                   log_id=log_id,
                   duration=session_data.duration_minutes,
                   calories_burned=calories_burned)
        
        return SuccessResponse(
            message="Sessão de treino registrada com sucesso",
            data={
                "log_id": log_id,
                "session_id": session_data.session_id,
                "duration_minutes": session_data.duration_minutes,
                "calories_burned": round(calories_burned, 1),
                "exercises_count": len(session_data.exercises_performed)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao registrar sessão de treino", 
                    user_id=current_user.get("user_id"),
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao registrar sessão de treino"
        )


@router.get("/history/{log_type}")
async def get_log_history(
    log_type: str,
    days: int = 7,
    current_user: Dict[str, Any] = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service)
):
    """
    Obtém histórico de logs de um tipo específico
    
    Args:
        log_type: Tipo de log (meal_checkin, set, body_weight, workout_session)
        days: Número de dias para buscar (padrão: 7)
    """
    try:
        user_id = current_user["user_id"]
        
        # Validar tipo de log
        try:
            LogType(log_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de log inválido: {log_type}"
            )
        
        # Validar número de dias
        if days <= 0 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Número de dias deve estar entre 1 e 365"
            )
        
        # Calcular período
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - days + 1)
        
        # Buscar logs
        logs = await firebase_service.get_logs_by_date_range(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            log_types=[log_type]
        )
        
        logger.info("Histórico de logs obtido", 
                   user_id=user_id,
                   log_type=log_type,
                   days=days,
                   count=len(logs))
        
        return {
            "success": True,
            "data": {
                "logs": logs,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "count": len(logs)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao obter histórico", 
                    user_id=current_user.get("user_id"),
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter histórico"
        )


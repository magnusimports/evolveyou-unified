"""
Rotas para analytics de progresso e visualização de dados
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import structlog
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import JSONResponse

from models.tracking import (
    ProgressSummaryResponse, WeightDataPoint, StrengthDataPoint, 
    ProgressChart, ProgressMetric, TrendDirection
)
from services.firebase_service import FirebaseService
from services.cache_service import CacheService
from services.calorie_service import CalorieService
from middleware.auth import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()


def get_firebase_service(request: Request) -> FirebaseService:
    """Dependency para obter serviço Firebase"""
    return request.app.state.firebase


def get_cache_service(request: Request) -> CacheService:
    """Dependency para obter serviço de cache"""
    return request.app.state.cache


def get_calorie_service(request: Request) -> CalorieService:
    """Dependency para obter serviço de cálculo calórico"""
    if not hasattr(request.app.state, 'calorie_service'):
        request.app.state.calorie_service = CalorieService(
            firebase_service=request.app.state.firebase
        )
    return request.app.state.calorie_service


@router.get("/summary", response_model=ProgressSummaryResponse)
async def get_progress_summary(
    days: int = Query(30, ge=7, le=365, description="Número de dias para análise (7-365)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
    cache_service: CacheService = Depends(get_cache_service),
    calorie_service: CalorieService = Depends(get_calorie_service)
):
    """
    Endpoint de analytics de progresso
    
    Este endpoint consulta o histórico de logs do usuário e formata
    os dados em estruturas otimizadas para gráficos e visualizações,
    incluindo:
    - Histórico de peso corporal com tendências
    - Progressão de força por exercício
    - Métricas de performance
    - Conquistas do período
    """
    try:
        user_id = current_user["user_id"]
        
        logger.info("Iniciando análise de progresso", 
                   user_id=user_id,
                   days=days)
        
        # Verificar cache primeiro
        cached_progress = await cache_service.get_progress_cache(user_id, days)
        if cached_progress:
            logger.info("Progresso obtido do cache", user_id=user_id, days=days)
            return ProgressSummaryResponse(**cached_progress)
        
        # Calcular período de análise
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        
        # Executar consultas em paralelo para otimizar performance
        tasks = [
            # 1. Histórico de peso
            firebase_service.get_weight_history(user_id, days),
            
            # 2. Progresso de força
            firebase_service.get_strength_progress(user_id, days),
            
            # 3. Logs gerais para métricas adicionais
            firebase_service.get_logs_by_date_range(
                user_id, start_date, end_date
            )
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            weight_history, strength_history, all_logs = results
            
            # Tratar exceções individuais
            if isinstance(weight_history, Exception):
                logger.warning("Erro ao obter histórico de peso", error=str(weight_history))
                weight_history = []
            
            if isinstance(strength_history, Exception):
                logger.warning("Erro ao obter progresso de força", error=str(strength_history))
                strength_history = []
            
            if isinstance(all_logs, Exception):
                logger.warning("Erro ao obter logs gerais", error=str(all_logs))
                all_logs = []
                
        except Exception as e:
            logger.error("Erro nas consultas paralelas", error=str(e))
            raise HTTPException(
                status_code=500,
                detail="Erro ao obter dados históricos"
            )
        
        # Processar dados de peso
        weight_progress = await _process_weight_data(weight_history)
        
        # Processar dados de força
        strength_progress = await _process_strength_data(strength_history, calorie_service)
        
        # Gerar gráficos otimizados
        charts = await _generate_progress_charts(
            weight_progress, strength_progress, all_logs, days
        )
        
        # Calcular métricas principais
        key_metrics = await _calculate_key_metrics(
            weight_progress, strength_progress, all_logs, days
        )
        
        # Identificar conquistas
        achievements = await _identify_achievements(
            weight_progress, strength_progress, all_logs, days
        )
        
        # Construir resposta
        progress_response = ProgressSummaryResponse(
            user_id=user_id,
            period_start=start_date,
            period_end=end_date,
            weight_progress=weight_progress,
            strength_progress=strength_progress,
            charts=charts,
            key_metrics=key_metrics,
            achievements=achievements
        )
        
        # Salvar no cache
        await cache_service.set_progress_cache(
            user_id, days, progress_response.dict()
        )
        
        logger.info("Análise de progresso concluída", 
                   user_id=user_id,
                   days=days,
                   weight_points=len(weight_progress),
                   strength_points=len(strength_progress),
                   charts_count=len(charts))
        
        return progress_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao gerar análise de progresso", 
                    user_id=current_user.get("user_id"),
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao gerar análise de progresso"
        )


async def _process_weight_data(weight_history: List[Dict[str, Any]]) -> List[WeightDataPoint]:
    """Processa dados de peso em pontos de dados estruturados"""
    
    weight_points = []
    
    for entry in weight_history:
        try:
            # Converter string de data para objeto date
            if isinstance(entry["date"], str):
                entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            else:
                entry_date = entry["date"]
            
            weight_point = WeightDataPoint(
                date=entry_date,
                weight_kg=entry["weight_kg"],
                body_fat_percentage=entry.get("body_fat_percentage"),
                muscle_mass_kg=entry.get("muscle_mass_kg")
            )
            weight_points.append(weight_point)
            
        except Exception as e:
            logger.warning("Erro ao processar entrada de peso", 
                          entry=entry, error=str(e))
            continue
    
    # Ordenar por data
    weight_points.sort(key=lambda x: x.date)
    
    logger.info("Dados de peso processados", count=len(weight_points))
    return weight_points


async def _process_strength_data(
    strength_history: List[Dict[str, Any]], 
    calorie_service: CalorieService
) -> List[StrengthDataPoint]:
    """Processa dados de força em pontos de dados estruturados"""
    
    strength_points = []
    
    # Agrupar por exercício e data para calcular máximos diários
    exercise_daily_max = defaultdict(lambda: defaultdict(list))
    
    for entry in strength_history:
        try:
            # Converter string de data para objeto date
            if isinstance(entry["date"], str):
                entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            else:
                entry_date = entry["date"]
            
            exercise_id = entry["exercise_id"]
            weight_kg = entry.get("weight_kg", 0)
            reps_done = entry.get("reps_done", 0)
            
            if weight_kg > 0 and reps_done > 0:
                exercise_daily_max[exercise_id][entry_date].append({
                    "weight_kg": weight_kg,
                    "reps_done": reps_done,
                    "exercise_name": entry.get("exercise_name", "Exercício"),
                    "volume": weight_kg * reps_done
                })
                
        except Exception as e:
            logger.warning("Erro ao processar entrada de força", 
                          entry=entry, error=str(e))
            continue
    
    # Calcular pontos de dados de força
    for exercise_id, daily_data in exercise_daily_max.items():
        for entry_date, sets in daily_data.items():
            try:
                # Encontrar peso máximo do dia
                max_weight_set = max(sets, key=lambda x: x["weight_kg"])
                max_weight_kg = max_weight_set["weight_kg"]
                
                # Calcular volume total do dia
                total_volume_kg = sum(s["volume"] for s in sets)
                
                # Estimar 1RM usando o melhor set do dia
                best_set = max(sets, key=lambda x: x["weight_kg"] * x["reps_done"])
                one_rep_max = await calorie_service.estimate_one_rep_max(
                    best_set["weight_kg"], best_set["reps_done"]
                )
                
                strength_point = StrengthDataPoint(
                    date=entry_date,
                    exercise_id=exercise_id,
                    exercise_name=max_weight_set["exercise_name"],
                    max_weight_kg=max_weight_kg,
                    total_volume_kg=total_volume_kg,
                    one_rep_max_estimated=one_rep_max
                )
                strength_points.append(strength_point)
                
            except Exception as e:
                logger.warning("Erro ao calcular ponto de força", 
                              exercise_id=exercise_id, date=entry_date, error=str(e))
                continue
    
    # Ordenar por data
    strength_points.sort(key=lambda x: x.date)
    
    logger.info("Dados de força processados", count=len(strength_points))
    return strength_points


async def _generate_progress_charts(
    weight_progress: List[WeightDataPoint],
    strength_progress: List[StrengthDataPoint],
    all_logs: List[Dict[str, Any]],
    days: int
) -> List[ProgressChart]:
    """Gera gráficos otimizados para visualização"""
    
    charts = []
    
    # 1. Gráfico de peso corporal
    if weight_progress:
        weight_data_points = [
            {
                "x": point.date.isoformat(),
                "y": point.weight_kg,
                "label": f"{point.weight_kg}kg"
            }
            for point in weight_progress
        ]
        
        # Calcular linha de tendência simples
        if len(weight_progress) >= 2:
            first_weight = weight_progress[0].weight_kg
            last_weight = weight_progress[-1].weight_kg
            trend_line = [
                {"x": weight_progress[0].date.isoformat(), "y": first_weight},
                {"x": weight_progress[-1].date.isoformat(), "y": last_weight}
            ]
        else:
            trend_line = None
        
        weight_chart = ProgressChart(
            chart_type="weight",
            title="Evolução do Peso Corporal",
            x_axis_label="Data",
            y_axis_label="Peso (kg)",
            data_points=weight_data_points,
            trend_line=trend_line,
            annotations=[
                {
                    "type": "goal",
                    "text": f"Variação: {last_weight - first_weight:+.1f}kg" if len(weight_progress) >= 2 else ""
                }
            ]
        )
        charts.append(weight_chart)
    
    # 2. Gráfico de força (exercício com mais dados)
    if strength_progress:
        # Agrupar por exercício
        exercise_groups = defaultdict(list)
        for point in strength_progress:
            exercise_groups[point.exercise_id].append(point)
        
        # Pegar exercício com mais pontos de dados
        best_exercise = max(exercise_groups.items(), key=lambda x: len(x[1]))
        exercise_id, exercise_points = best_exercise
        
        if len(exercise_points) >= 2:
            strength_data_points = [
                {
                    "x": point.date.isoformat(),
                    "y": point.max_weight_kg,
                    "label": f"{point.max_weight_kg}kg"
                }
                for point in exercise_points
            ]
            
            # Linha de tendência
            first_weight = exercise_points[0].max_weight_kg
            last_weight = exercise_points[-1].max_weight_kg
            trend_line = [
                {"x": exercise_points[0].date.isoformat(), "y": first_weight},
                {"x": exercise_points[-1].date.isoformat(), "y": last_weight}
            ]
            
            strength_chart = ProgressChart(
                chart_type="strength",
                title=f"Progressão de Força - {exercise_points[0].exercise_name}",
                x_axis_label="Data",
                y_axis_label="Peso Máximo (kg)",
                data_points=strength_data_points,
                trend_line=trend_line,
                annotations=[
                    {
                        "type": "progress",
                        "text": f"Progresso: {last_weight - first_weight:+.1f}kg"
                    }
                ]
            )
            charts.append(strength_chart)
    
    # 3. Gráfico de volume de treino semanal
    workout_volume_chart = await _generate_volume_chart(all_logs, days)
    if workout_volume_chart:
        charts.append(workout_volume_chart)
    
    logger.info("Gráficos gerados", count=len(charts))
    return charts


async def _generate_volume_chart(all_logs: List[Dict[str, Any]], days: int) -> Optional[ProgressChart]:
    """Gera gráfico de volume de treino"""
    
    try:
        # Agrupar logs de séries por semana
        weekly_volume = defaultdict(float)
        
        for log in all_logs:
            if log.get("log_type") == "set":
                log_date = datetime.strptime(log["date"], "%Y-%m-%d").date()
                # Calcular início da semana (segunda-feira)
                week_start = log_date - timedelta(days=log_date.weekday())
                
                weight = log.get("value", {}).get("weight_kg", 0)
                reps = log.get("value", {}).get("reps_done", 0)
                volume = weight * reps
                
                weekly_volume[week_start] += volume
        
        if not weekly_volume:
            return None
        
        # Converter para pontos de dados
        volume_data_points = [
            {
                "x": week_start.isoformat(),
                "y": round(volume, 1),
                "label": f"{volume:.0f}kg"
            }
            for week_start, volume in sorted(weekly_volume.items())
        ]
        
        return ProgressChart(
            chart_type="volume",
            title="Volume de Treino Semanal",
            x_axis_label="Semana",
            y_axis_label="Volume Total (kg)",
            data_points=volume_data_points,
            annotations=[
                {
                    "type": "info",
                    "text": f"Média: {sum(weekly_volume.values()) / len(weekly_volume):.0f}kg/semana"
                }
            ]
        )
        
    except Exception as e:
        logger.error("Erro ao gerar gráfico de volume", error=str(e))
        return None


async def _calculate_key_metrics(
    weight_progress: List[WeightDataPoint],
    strength_progress: List[StrengthDataPoint],
    all_logs: List[Dict[str, Any]],
    days: int
) -> List[ProgressMetric]:
    """Calcula métricas principais de progresso"""
    
    metrics = []
    
    try:
        # Métrica de peso
        if len(weight_progress) >= 2:
            first_weight = weight_progress[0].weight_kg
            last_weight = weight_progress[-1].weight_kg
            weight_change = last_weight - first_weight
            weight_change_percentage = (weight_change / first_weight * 100) if first_weight > 0 else 0
            
            trend = TrendDirection.DOWN if weight_change < -0.1 else TrendDirection.UP if weight_change > 0.1 else TrendDirection.STABLE
            
            metrics.append(ProgressMetric(
                metric_name="Peso Corporal",
                current_value=last_weight,
                previous_value=first_weight,
                change_value=weight_change,
                change_percentage=weight_change_percentage,
                trend=trend,
                unit="kg",
                last_updated=datetime.utcnow()
            ))
        
        # Métrica de força (exercício com maior progresso)
        if strength_progress:
            exercise_progress = defaultdict(list)
            for point in strength_progress:
                exercise_progress[point.exercise_id].append(point)
            
            best_progress = None
            best_improvement = 0
            
            for exercise_id, points in exercise_progress.items():
                if len(points) >= 2:
                    points.sort(key=lambda x: x.date)
                    first_weight = points[0].max_weight_kg
                    last_weight = points[-1].max_weight_kg
                    improvement = last_weight - first_weight
                    
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_progress = {
                            "name": points[-1].exercise_name,
                            "first": first_weight,
                            "last": last_weight,
                            "change": improvement
                        }
            
            if best_progress:
                change_percentage = (best_progress["change"] / best_progress["first"] * 100) if best_progress["first"] > 0 else 0
                
                metrics.append(ProgressMetric(
                    metric_name=f"Força - {best_progress['name']}",
                    current_value=best_progress["last"],
                    previous_value=best_progress["first"],
                    change_value=best_progress["change"],
                    change_percentage=change_percentage,
                    trend=TrendDirection.UP if best_progress["change"] > 0 else TrendDirection.STABLE,
                    unit="kg",
                    last_updated=datetime.utcnow()
                ))
        
        # Métrica de consistência
        workout_days = len(set(
            log["date"] for log in all_logs 
            if log.get("log_type") in ["set", "workout_session"]
        ))
        
        consistency_percentage = (workout_days / days * 100) if days > 0 else 0
        
        metrics.append(ProgressMetric(
            metric_name="Consistência de Treino",
            current_value=workout_days,
            previous_value=None,
            change_value=None,
            change_percentage=consistency_percentage,
            trend=TrendDirection.UP if consistency_percentage >= 70 else TrendDirection.STABLE,
            unit="dias",
            last_updated=datetime.utcnow()
        ))
        
    except Exception as e:
        logger.error("Erro ao calcular métricas", error=str(e))
    
    logger.info("Métricas calculadas", count=len(metrics))
    return metrics


async def _identify_achievements(
    weight_progress: List[WeightDataPoint],
    strength_progress: List[StrengthDataPoint],
    all_logs: List[Dict[str, Any]],
    days: int
) -> List[str]:
    """Identifica conquistas do período"""
    
    achievements = []
    
    try:
        # Conquista de peso
        if len(weight_progress) >= 2:
            weight_change = weight_progress[-1].weight_kg - weight_progress[0].weight_kg
            if abs(weight_change) >= 1.0:
                if weight_change < 0:
                    achievements.append(f"🎯 Perdeu {abs(weight_change):.1f}kg no período!")
                else:
                    achievements.append(f"💪 Ganhou {weight_change:.1f}kg no período!")
        
        # Conquista de força
        exercise_improvements = defaultdict(list)
        for point in strength_progress:
            exercise_improvements[point.exercise_id].append(point.max_weight_kg)
        
        for exercise_id, weights in exercise_improvements.items():
            if len(weights) >= 2:
                improvement = max(weights) - min(weights)
                if improvement >= 5.0:  # Melhoria significativa
                    exercise_name = next(
                        (p.exercise_name for p in strength_progress if p.exercise_id == exercise_id),
                        "Exercício"
                    )
                    achievements.append(f"🏋️ Aumentou {improvement:.1f}kg no {exercise_name}!")
        
        # Conquista de consistência
        workout_days = len(set(
            log["date"] for log in all_logs 
            if log.get("log_type") in ["set", "workout_session"]
        ))
        
        if workout_days >= days * 0.8:  # 80% de consistência
            achievements.append(f"🔥 Treinou {workout_days} de {days} dias - Excelente consistência!")
        elif workout_days >= days * 0.6:  # 60% de consistência
            achievements.append(f"👏 Treinou {workout_days} de {days} dias - Boa consistência!")
        
        # Conquista de volume
        total_sets = len([log for log in all_logs if log.get("log_type") == "set"])
        if total_sets >= 100:
            achievements.append(f"💯 Completou {total_sets} séries no período!")
        
        # Conquista de refeições
        meal_logs = len([log for log in all_logs if log.get("log_type") == "meal_checkin"])
        if meal_logs >= days * 3:  # Pelo menos 3 refeições por dia em média
            achievements.append("🍽️ Manteve excelente disciplina alimentar!")
        
    except Exception as e:
        logger.error("Erro ao identificar conquistas", error=str(e))
    
    # Limitar a 5 conquistas principais
    achievements = achievements[:5]
    
    logger.info("Conquistas identificadas", count=len(achievements))
    return achievements


@router.get("/weight-trend")
async def get_weight_trend(
    days: int = Query(30, ge=7, le=90, description="Número de dias para análise de tendência"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service)
):
    """
    Obtém tendência de peso corporal
    
    Retorna análise específica da evolução do peso com métricas detalhadas
    """
    try:
        user_id = current_user["user_id"]
        
        # Obter histórico de peso
        weight_history = await firebase_service.get_weight_history(user_id, days)
        
        if not weight_history:
            return {
                "success": True,
                "data": {
                    "trend": "no_data",
                    "message": "Nenhum dado de peso encontrado"
                }
            }
        
        # Calcular estatísticas
        weights = [entry["weight_kg"] for entry in weight_history]
        
        current_weight = weights[-1]
        initial_weight = weights[0]
        min_weight = min(weights)
        max_weight = max(weights)
        avg_weight = sum(weights) / len(weights)
        
        weight_change = current_weight - initial_weight
        weight_change_percentage = (weight_change / initial_weight * 100) if initial_weight > 0 else 0
        
        # Determinar tendência
        if weight_change < -0.5:
            trend = "decreasing"
            trend_message = f"Tendência de perda: {abs(weight_change):.1f}kg"
        elif weight_change > 0.5:
            trend = "increasing"
            trend_message = f"Tendência de ganho: {weight_change:.1f}kg"
        else:
            trend = "stable"
            trend_message = "Peso estável"
        
        return {
            "success": True,
            "data": {
                "trend": trend,
                "trend_message": trend_message,
                "current_weight": current_weight,
                "initial_weight": initial_weight,
                "weight_change": weight_change,
                "weight_change_percentage": round(weight_change_percentage, 2),
                "min_weight": min_weight,
                "max_weight": max_weight,
                "avg_weight": round(avg_weight, 1),
                "data_points": len(weight_history),
                "period_days": days
            }
        }
        
    except Exception as e:
        logger.error("Erro ao obter tendência de peso", 
                    user_id=current_user.get("user_id"),
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter tendência de peso"
        )


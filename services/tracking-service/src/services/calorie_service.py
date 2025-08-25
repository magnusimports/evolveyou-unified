"""
Serviço para cálculos de gasto calórico e balanço energético
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
import structlog
import math

from config.settings import get_settings

logger = structlog.get_logger(__name__)


class CalorieService:
    """Serviço para cálculos relacionados a calorias e balanço energético"""
    
    def __init__(self, firebase_service=None):
        self.settings = get_settings()
        self.firebase_service = firebase_service
        self.config = self.settings.tracking_config["calorie_calculation"]
    
    async def calculate_workout_calories(
        self,
        user_weight: float,
        duration_minutes: int,
        met_values: Dict[str, float],
        intensity_factor: float = 1.0
    ) -> float:
        """
        Calcula gasto calórico de uma sessão de treino
        
        Fórmula: Calorias = MET × peso(kg) × tempo(h) × fator_intensidade
        
        Args:
            user_weight: Peso do usuário em kg
            duration_minutes: Duração do treino em minutos
            met_values: Valores MET dos exercícios realizados
            intensity_factor: Fator de intensidade (0.5 a 1.5)
            
        Returns:
            float: Calorias queimadas
        """
        try:
            # Converter duração para horas
            duration_hours = duration_minutes / 60.0
            
            # Calcular MET médio dos exercícios
            if met_values:
                average_met = sum(met_values.values()) / len(met_values)
            else:
                average_met = self.config["default_met_value"]
            
            # Aplicar fatores de configuração
            met_multiplier = self.config["met_multiplier"]
            duration_factor = self.config["duration_factor"]
            weight_factor = self.config["weight_factor"]
            
            # Calcular calorias base
            calories_base = (
                average_met * 
                user_weight * weight_factor * 
                duration_hours * duration_factor * 
                met_multiplier
            )
            
            # Aplicar fator de intensidade
            calories_total = calories_base * intensity_factor
            
            logger.info("Cálculo de gasto calórico", 
                       user_weight=user_weight,
                       duration_minutes=duration_minutes,
                       average_met=average_met,
                       intensity_factor=intensity_factor,
                       calories_burned=calories_total)
            
            return max(0, calories_total)  # Garantir que não seja negativo
            
        except Exception as e:
            logger.error("Erro no cálculo de gasto calórico", 
                        error=str(e),
                        user_weight=user_weight,
                        duration_minutes=duration_minutes)
            # Retornar estimativa conservadora
            return duration_minutes * 5.0  # ~5 cal/min
    
    async def calculate_daily_energy_balance(
        self,
        user_id: str,
        target_date: date,
        user_bmr: float,
        user_tdee: float,
        daily_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcula o balanço energético do dia
        
        Args:
            user_id: ID do usuário
            target_date: Data alvo
            user_bmr: Taxa metabólica basal
            user_tdee: Gasto energético total diário
            daily_logs: Logs do dia
            
        Returns:
            Dict: Balanço energético detalhado
        """
        try:
            # Inicializar contadores
            calories_consumed = 0.0
            calories_burned_exercise = 0.0
            
            # Processar logs do dia
            for log in daily_logs:
                log_type = log.get("log_type")
                log_value = log.get("value", {})
                
                if log_type == "meal_checkin":
                    # Somar calorias consumidas
                    nutritional = log_value.get("nutritional_summary", {})
                    calories_consumed += nutritional.get("total_calories", 0)
                
                elif log_type == "workout_session":
                    # Somar calorias queimadas em exercícios
                    calories_burned_exercise += log_value.get("calories_burned", 0)
            
            # Calcular gasto total
            calories_out_total = user_tdee + calories_burned_exercise
            
            # Calcular balanço líquido
            net_balance = calories_consumed - calories_out_total
            
            # Determinar status do balanço
            balance_status = self._determine_balance_status(net_balance)
            
            # Calcular percentuais
            bmr_percentage = (user_bmr / calories_out_total * 100) if calories_out_total > 0 else 0
            activity_percentage = ((user_tdee - user_bmr) / calories_out_total * 100) if calories_out_total > 0 else 0
            exercise_percentage = (calories_burned_exercise / calories_out_total * 100) if calories_out_total > 0 else 0
            
            energy_balance = {
                "date": target_date.isoformat(),
                "calories_in": round(calories_consumed, 1),
                "calories_out": {
                    "total": round(calories_out_total, 1),
                    "bmr": round(user_bmr, 1),
                    "activity": round(user_tdee - user_bmr, 1),
                    "exercise": round(calories_burned_exercise, 1)
                },
                "net_balance": round(net_balance, 1),
                "balance_status": balance_status,
                "percentages": {
                    "bmr": round(bmr_percentage, 1),
                    "activity": round(activity_percentage, 1),
                    "exercise": round(exercise_percentage, 1)
                },
                "recommendations": self._generate_balance_recommendations(
                    net_balance, calories_consumed, calories_out_total
                )
            }
            
            logger.info("Balanço energético calculado", 
                       user_id=user_id,
                       date=target_date.isoformat(),
                       net_balance=net_balance,
                       status=balance_status)
            
            return energy_balance
            
        except Exception as e:
            logger.error("Erro no cálculo de balanço energético", 
                        error=str(e),
                        user_id=user_id,
                        date=target_date.isoformat())
            # Retornar balanço padrão
            return {
                "date": target_date.isoformat(),
                "calories_in": 0,
                "calories_out": {"total": user_tdee, "bmr": user_bmr, "activity": 0, "exercise": 0},
                "net_balance": -user_tdee,
                "balance_status": "deficit",
                "percentages": {"bmr": 100, "activity": 0, "exercise": 0},
                "recommendations": []
            }
    
    def _determine_balance_status(self, net_balance: float) -> str:
        """
        Determina o status do balanço energético
        
        Args:
            net_balance: Balanço líquido de calorias
            
        Returns:
            str: Status (deficit/surplus/maintenance)
        """
        if net_balance < -100:
            return "deficit"
        elif net_balance > 100:
            return "surplus"
        else:
            return "maintenance"
    
    def _generate_balance_recommendations(
        self,
        net_balance: float,
        calories_in: float,
        calories_out: float
    ) -> List[str]:
        """
        Gera recomendações baseadas no balanço energético
        
        Args:
            net_balance: Balanço líquido
            calories_in: Calorias consumidas
            calories_out: Calorias gastas
            
        Returns:
            List[str]: Lista de recomendações
        """
        recommendations = []
        
        if net_balance < -500:
            recommendations.append("Déficit muito alto. Considere aumentar a ingestão calórica.")
        elif net_balance < -200:
            recommendations.append("Bom déficit para perda de peso. Continue assim!")
        elif net_balance > 500:
            recommendations.append("Superávit alto. Reduza a ingestão ou aumente a atividade.")
        elif net_balance > 200:
            recommendations.append("Superávit moderado. Bom para ganho de massa.")
        else:
            recommendations.append("Balanço equilibrado. Ideal para manutenção.")
        
        # Recomendações específicas
        if calories_in < 1200:
            recommendations.append("Ingestão muito baixa. Certifique-se de comer o suficiente.")
        
        if calories_out - calories_in > 1000:
            recommendations.append("Grande déficit. Monitore energia e recuperação.")
        
        return recommendations
    
    async def calculate_macronutrient_balance(
        self,
        daily_logs: List[Dict[str, Any]],
        targets: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calcula o balanço de macronutrientes do dia
        
        Args:
            daily_logs: Logs de refeições do dia
            targets: Metas de macronutrientes
            
        Returns:
            Dict: Balanço de macronutrientes
        """
        try:
            # Inicializar contadores
            consumed = {"protein": 0.0, "carbs": 0.0, "fat": 0.0, "calories": 0.0}
            
            # Somar macros consumidos
            for log in daily_logs:
                if log.get("log_type") == "meal_checkin":
                    nutritional = log.get("value", {}).get("nutritional_summary", {})
                    consumed["protein"] += nutritional.get("total_protein", 0)
                    consumed["carbs"] += nutritional.get("total_carbs", 0)
                    consumed["fat"] += nutritional.get("total_fat", 0)
                    consumed["calories"] += nutritional.get("total_calories", 0)
            
            # Calcular percentuais e diferenças
            macro_balance = {}
            
            for macro in ["protein", "carbs", "fat", "calories"]:
                target = targets.get(macro, 0)
                current = consumed[macro]
                
                remaining = max(0, target - current)
                percentage = (current / target * 100) if target > 0 else 0
                
                macro_balance[macro] = {
                    "target": round(target, 1),
                    "consumed": round(current, 1),
                    "remaining": round(remaining, 1),
                    "percentage": round(percentage, 1),
                    "status": self._get_macro_status(percentage)
                }
            
            logger.info("Balanço de macronutrientes calculado", 
                       consumed=consumed,
                       targets=targets)
            
            return macro_balance
            
        except Exception as e:
            logger.error("Erro no cálculo de macronutrientes", error=str(e))
            return {}
    
    def _get_macro_status(self, percentage: float) -> str:
        """
        Determina o status de um macronutriente baseado no percentual atingido
        
        Args:
            percentage: Percentual atingido da meta
            
        Returns:
            str: Status (low/good/high/exceeded)
        """
        if percentage < 70:
            return "low"
        elif percentage <= 110:
            return "good"
        elif percentage <= 130:
            return "high"
        else:
            return "exceeded"
    
    async def estimate_one_rep_max(
        self,
        weight_kg: float,
        reps: int,
        formula: str = "brzycki"
    ) -> float:
        """
        Estima 1RM baseado em peso e repetições
        
        Args:
            weight_kg: Peso levantado
            reps: Número de repetições
            formula: Fórmula a usar (brzycki, epley, etc.)
            
        Returns:
            float: 1RM estimado
        """
        try:
            if reps == 1:
                return weight_kg
            
            if formula == "brzycki":
                # Fórmula de Brzycki: 1RM = peso / (1.0278 - 0.0278 × reps)
                one_rm = weight_kg / (1.0278 - 0.0278 * reps)
            elif formula == "epley":
                # Fórmula de Epley: 1RM = peso × (1 + reps/30)
                one_rm = weight_kg * (1 + reps / 30)
            else:
                # Padrão: Brzycki
                one_rm = weight_kg / (1.0278 - 0.0278 * reps)
            
            # Limitar a valores razoáveis
            one_rm = max(weight_kg, min(one_rm, weight_kg * 2))
            
            logger.debug("1RM estimado", 
                        weight=weight_kg,
                        reps=reps,
                        formula=formula,
                        one_rm=one_rm)
            
            return round(one_rm, 1)
            
        except Exception as e:
            logger.error("Erro no cálculo de 1RM", 
                        error=str(e),
                        weight=weight_kg,
                        reps=reps)
            return weight_kg  # Fallback
    
    async def calculate_training_volume(
        self,
        sets_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcula volume de treinamento
        
        Args:
            sets_data: Dados das séries realizadas
            
        Returns:
            Dict: Métricas de volume
        """
        try:
            total_sets = len(sets_data)
            total_reps = sum(s.get("reps_done", 0) for s in sets_data)
            total_weight = sum(
                s.get("weight_kg", 0) * s.get("reps_done", 0) 
                for s in sets_data
            )
            
            # Agrupar por exercício
            exercises = {}
            for set_data in sets_data:
                exercise_id = set_data.get("exercise_id")
                if exercise_id not in exercises:
                    exercises[exercise_id] = {
                        "sets": 0,
                        "reps": 0,
                        "volume": 0,
                        "max_weight": 0
                    }
                
                exercises[exercise_id]["sets"] += 1
                exercises[exercise_id]["reps"] += set_data.get("reps_done", 0)
                exercises[exercise_id]["volume"] += (
                    set_data.get("weight_kg", 0) * set_data.get("reps_done", 0)
                )
                exercises[exercise_id]["max_weight"] = max(
                    exercises[exercise_id]["max_weight"],
                    set_data.get("weight_kg", 0)
                )
            
            volume_metrics = {
                "total_sets": total_sets,
                "total_reps": total_reps,
                "total_volume_kg": round(total_weight, 1),
                "exercises_count": len(exercises),
                "exercises": exercises,
                "average_reps_per_set": round(total_reps / total_sets, 1) if total_sets > 0 else 0,
                "average_volume_per_set": round(total_weight / total_sets, 1) if total_sets > 0 else 0
            }
            
            logger.info("Volume de treinamento calculado", 
                       total_sets=total_sets,
                       total_volume=total_weight,
                       exercises=len(exercises))
            
            return volume_metrics
            
        except Exception as e:
            logger.error("Erro no cálculo de volume", error=str(e))
            return {
                "total_sets": 0,
                "total_reps": 0,
                "total_volume_kg": 0,
                "exercises_count": 0,
                "exercises": {},
                "average_reps_per_set": 0,
                "average_volume_per_set": 0
            }


"""
Cliente para comunicação entre microserviços
"""

import asyncio
from typing import Dict, Any, List, Optional
import structlog
import httpx
from datetime import datetime, timedelta

from config.settings import get_settings

logger = structlog.get_logger(__name__)


class ServiceClient:
    """Cliente para comunicação com outros microserviços"""
    
    def __init__(self):
        self.settings = get_settings()
        self.timeout = httpx.Timeout(
            timeout=self.settings.tracking_config["dashboard_config"]["timeout_seconds"]
        )
        self.max_retries = self.settings.tracking_config["dashboard_config"]["max_retries"]
        
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Faz uma requisição HTTP com retry automático
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            url: URL completa
            headers: Headers da requisição
            json_data: Dados JSON para POST/PUT
            params: Parâmetros de query
            
        Returns:
            Dict: Resposta JSON
            
        Raises:
            Exception: Se todas as tentativas falharem
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=json_data,
                        params=params
                    )
                    
                    # Log da requisição
                    logger.info("Requisição para serviço", 
                               method=method,
                               url=url,
                               status_code=response.status_code,
                               attempt=attempt + 1)
                    
                    # Verificar se a resposta foi bem-sucedida
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 404:
                        logger.warning("Recurso não encontrado", url=url)
                        return {}
                    else:
                        response.raise_for_status()
                        
            except Exception as e:
                last_exception = e
                logger.warning("Falha na requisição", 
                              method=method,
                              url=url,
                              attempt=attempt + 1,
                              error=str(e))
                
                # Se não é a última tentativa, aguardar antes de tentar novamente
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Backoff exponencial
        
        # Se chegou aqui, todas as tentativas falharam
        logger.error("Todas as tentativas falharam", 
                    method=method,
                    url=url,
                    error=str(last_exception))
        raise last_exception
    
    # Métodos para Users Service
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém perfil do usuário do Users Service
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict: Dados do perfil do usuário
        """
        try:
            url = f"{self.settings.users_service_url}/user/profile-summary"
            headers = {"X-User-ID": user_id}
            
            response = await self._make_request("GET", url, headers=headers)
            
            logger.info("Perfil do usuário obtido", user_id=user_id)
            return response.get("data", {})
            
        except Exception as e:
            logger.error("Erro ao obter perfil do usuário", 
                        user_id=user_id,
                        error=str(e))
            # Retornar dados padrão em caso de falha
            return {
                "nickname": "Usuário",
                "weight_kg": 70,
                "bmr": 1800,
                "tdee": 2200
            }
    
    async def get_user_goals(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém objetivos do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict: Objetivos do usuário
        """
        try:
            url = f"{self.settings.users_service_url}/user/goals"
            headers = {"X-User-ID": user_id}
            
            response = await self._make_request("GET", url, headers=headers)
            
            logger.info("Objetivos do usuário obtidos", user_id=user_id)
            return response.get("data", {})
            
        except Exception as e:
            logger.error("Erro ao obter objetivos do usuário", 
                        user_id=user_id,
                        error=str(e))
            return {}
    
    # Métodos para Plans Service
    
    async def get_daily_targets(self, user_id: str, date: str = None) -> Dict[str, Any]:
        """
        Obtém metas diárias do Plans Service
        
        Args:
            user_id: ID do usuário
            date: Data no formato YYYY-MM-DD (opcional, padrão hoje)
            
        Returns:
            Dict: Metas diárias de calorias e macros
        """
        try:
            url = f"{self.settings.plans_service_url}/plan/targets"
            headers = {"X-User-ID": user_id}
            params = {"date": date} if date else {}
            
            response = await self._make_request("GET", url, headers=headers, params=params)
            
            logger.info("Metas diárias obtidas", user_id=user_id, date=date)
            return response.get("data", {})
            
        except Exception as e:
            logger.error("Erro ao obter metas diárias", 
                        user_id=user_id,
                        date=date,
                        error=str(e))
            # Retornar metas padrão em caso de falha
            return {
                "calories": 2000,
                "protein": 150,
                "carbs": 200,
                "fat": 67,
                "water_ml": 2500
            }
    
    async def get_workout_plan(self, user_id: str, date: str = None) -> Dict[str, Any]:
        """
        Obtém plano de treino do dia
        
        Args:
            user_id: ID do usuário
            date: Data no formato YYYY-MM-DD (opcional, padrão hoje)
            
        Returns:
            Dict: Plano de treino do dia
        """
        try:
            url = f"{self.settings.plans_service_url}/plan/workout"
            headers = {"X-User-ID": user_id}
            params = {"date": date} if date else {}
            
            response = await self._make_request("GET", url, headers=headers, params=params)
            
            logger.info("Plano de treino obtido", user_id=user_id, date=date)
            return response.get("data", {})
            
        except Exception as e:
            logger.error("Erro ao obter plano de treino", 
                        user_id=user_id,
                        date=date,
                        error=str(e))
            return {}
    
    async def get_meal_plan(self, user_id: str, date: str = None) -> Dict[str, Any]:
        """
        Obtém plano de refeições do dia
        
        Args:
            user_id: ID do usuário
            date: Data no formato YYYY-MM-DD (opcional, padrão hoje)
            
        Returns:
            Dict: Plano de refeições do dia
        """
        try:
            url = f"{self.settings.plans_service_url}/plan/diet"
            headers = {"X-User-ID": user_id}
            params = {"date": date} if date else {}
            
            response = await self._make_request("GET", url, headers=headers, params=params)
            
            logger.info("Plano de refeições obtido", user_id=user_id, date=date)
            return response.get("data", {})
            
        except Exception as e:
            logger.error("Erro ao obter plano de refeições", 
                        user_id=user_id,
                        date=date,
                        error=str(e))
            return {}
    
    # Métodos para Content Service
    
    async def get_exercise_met_values(self, exercise_ids: List[str]) -> Dict[str, float]:
        """
        Obtém valores MET dos exercícios do Content Service
        
        Args:
            exercise_ids: Lista de IDs dos exercícios
            
        Returns:
            Dict: Mapeamento exercise_id -> valor MET
        """
        try:
            url = f"{self.settings.content_service_url}/exercises/met-values"
            params = {"exercise_ids": ",".join(exercise_ids)}
            
            response = await self._make_request("GET", url, params=params)
            
            met_values = response.get("data", {}).get("met_values", {})
            
            logger.info("Valores MET obtidos", 
                       exercise_count=len(exercise_ids),
                       met_count=len(met_values))
            
            # Garantir que todos os exercícios tenham um valor MET
            default_met = self.settings.tracking_config["calorie_calculation"]["default_met_value"]
            for exercise_id in exercise_ids:
                if exercise_id not in met_values:
                    met_values[exercise_id] = default_met
                    logger.warning("Usando valor MET padrão", 
                                  exercise_id=exercise_id,
                                  default_met=default_met)
            
            return met_values
            
        except Exception as e:
            logger.error("Erro ao obter valores MET", 
                        exercise_ids=exercise_ids,
                        error=str(e))
            # Retornar valores padrão para todos os exercícios
            default_met = self.settings.tracking_config["calorie_calculation"]["default_met_value"]
            return {exercise_id: default_met for exercise_id in exercise_ids}
    
    async def get_food_details(self, food_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Obtém detalhes dos alimentos do Content Service
        
        Args:
            food_ids: Lista de IDs dos alimentos
            
        Returns:
            Dict: Mapeamento food_id -> detalhes do alimento
        """
        try:
            url = f"{self.settings.content_service_url}/foods/details"
            params = {"food_ids": ",".join(food_ids)}
            
            response = await self._make_request("GET", url, params=params)
            
            food_details = response.get("data", {}).get("foods", {})
            
            logger.info("Detalhes dos alimentos obtidos", 
                       food_count=len(food_ids),
                       details_count=len(food_details))
            
            return food_details
            
        except Exception as e:
            logger.error("Erro ao obter detalhes dos alimentos", 
                        food_ids=food_ids,
                        error=str(e))
            return {}
    
    # Métodos de health check
    
    async def check_service_health(self, service_name: str, service_url: str) -> bool:
        """
        Verifica se um serviço está saudável
        
        Args:
            service_name: Nome do serviço
            service_url: URL base do serviço
            
        Returns:
            bool: True se o serviço está saudável
        """
        try:
            url = f"{service_url}/health"
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                response = await client.get(url)
                
                is_healthy = response.status_code == 200
                
                logger.info("Health check do serviço", 
                           service=service_name,
                           healthy=is_healthy,
                           status_code=response.status_code)
                
                return is_healthy
                
        except Exception as e:
            logger.warning("Falha no health check", 
                          service=service_name,
                          error=str(e))
            return False
    
    async def check_all_services_health(self) -> Dict[str, bool]:
        """
        Verifica saúde de todos os serviços
        
        Returns:
            Dict: Status de saúde de cada serviço
        """
        services = {
            "users_service": self.settings.users_service_url,
            "content_service": self.settings.content_service_url,
            "plans_service": self.settings.plans_service_url
        }
        
        health_status = {}
        
        # Verificar todos os serviços em paralelo
        tasks = [
            self.check_service_health(name, url) 
            for name, url in services.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for (service_name, _), result in zip(services.items(), results):
            if isinstance(result, Exception):
                health_status[service_name] = False
                logger.error("Erro no health check", 
                           service=service_name,
                           error=str(result))
            else:
                health_status[service_name] = result
        
        logger.info("Health check completo", health_status=health_status)
        return health_status


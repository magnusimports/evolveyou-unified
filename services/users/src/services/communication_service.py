"""
Serviço de comunicação entre microserviços
"""

import json
import httpx
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

from config.settings import get_settings
from models.user import FitnessGoals, CalorieCalculation
from services.firebase_service import FirebaseService

logger = structlog.get_logger()
settings = get_settings()

class CommunicationService:
    """Serviço para comunicação entre microserviços"""
    
    def __init__(self):
        self.firebase_service = None
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def set_firebase_service(self, firebase_service: FirebaseService):
        """Definir serviço Firebase"""
        self.firebase_service = firebase_service
    
    async def notify_onboarding_completed(
        self,
        user_id: str,
        fitness_goals: FitnessGoals,
        calorie_calculation: CalorieCalculation
    ) -> bool:
        """
        Notificar outros serviços que o onboarding foi concluído
        
        Este método dispara eventos para:
        1. Serviço de Planos - para gerar planos iniciais
        2. Serviço de Notificações - para configurar notificações
        3. Sistema de Analytics - para tracking
        """
        try:
            logger.info("Iniciando notificação de onboarding concluído", user_id=user_id)
            
            # Preparar dados do evento
            event_data = {
                "event_type": "onboarding_completed",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "fitness_goals": fitness_goals.dict(),
                    "calorie_calculation": calorie_calculation.dict(),
                    "primary_goal": fitness_goals.primary_goal,
                    "training_experience": fitness_goals.training_experience,
                    "available_days": fitness_goals.available_days_per_week,
                    "maintenance_calories": calorie_calculation.maintenance_calories,
                    "bmr": calorie_calculation.bmr,
                    "tdee": calorie_calculation.tdee
                }
            }
            
            # 1. Salvar evento no Firestore para auditoria
            await self._save_event_to_firestore(event_data)
            
            # 2. Notificar Serviço de Planos (se disponível)
            await self._notify_plans_service(event_data)
            
            # 3. Notificar Serviço de Notificações (se disponível)
            await self._notify_notifications_service(event_data)
            
            # 4. Notificar Analytics (se disponível)
            await self._notify_analytics_service(event_data)
            
            # 5. Publicar no Pub/Sub (se configurado)
            await self._publish_to_pubsub(event_data)
            
            logger.info("Notificação de onboarding enviada com sucesso", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao notificar onboarding concluído", error=str(e), user_id=user_id)
            # Não falhar o onboarding por erro de comunicação
            return False
    
    async def _save_event_to_firestore(self, event_data: Dict[str, Any]) -> bool:
        """Salvar evento no Firestore para auditoria"""
        try:
            if not self.firebase_service:
                logger.warning("Firebase service não disponível para salvar evento")
                return False
            
            doc_ref = self.firebase_service.db.collection('system_events').document()
            event_data['id'] = doc_ref.id
            doc_ref.set(event_data)
            
            logger.info("Evento salvo no Firestore", event_id=doc_ref.id)
            return True
            
        except Exception as e:
            logger.error("Erro ao salvar evento no Firestore", error=str(e))
            return False
    
    async def _notify_plans_service(self, event_data: Dict[str, Any]) -> bool:
        """Notificar serviço de planos"""
        try:
            plans_service_url = settings.plans_service_url
            
            if not plans_service_url:
                logger.info("URL do serviço de planos não configurada")
                return False
            
            # Preparar payload específico para o serviço de planos
            payload = {
                "user_id": event_data["user_id"],
                "event_type": "generate_initial_plans",
                "fitness_goals": event_data["data"]["fitness_goals"],
                "calorie_calculation": event_data["data"]["calorie_calculation"],
                "timestamp": event_data["timestamp"]
            }
            
            # Fazer chamada HTTP para o serviço de planos
            response = await self.http_client.post(
                f"{plans_service_url}/events/onboarding-completed",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Service-Name": "users-service",
                    "X-Event-Type": "onboarding_completed"
                }
            )
            
            if response.status_code == 200:
                logger.info("Serviço de planos notificado com sucesso", user_id=event_data["user_id"])
                return True
            else:
                logger.warning(
                    "Erro ao notificar serviço de planos",
                    status_code=response.status_code,
                    response=response.text
                )
                return False
                
        except httpx.TimeoutException:
            logger.warning("Timeout ao notificar serviço de planos")
            return False
        except Exception as e:
            logger.error("Erro ao notificar serviço de planos", error=str(e))
            return False
    
    async def _notify_notifications_service(self, event_data: Dict[str, Any]) -> bool:
        """Notificar serviço de notificações"""
        try:
            notifications_service_url = settings.notifications_service_url
            
            if not notifications_service_url:
                logger.info("URL do serviço de notificações não configurada")
                return False
            
            # Preparar payload para configurar notificações iniciais
            payload = {
                "user_id": event_data["user_id"],
                "event_type": "setup_initial_notifications",
                "preferences": {
                    "workout_reminders": True,
                    "meal_reminders": True,
                    "progress_check_ins": True,
                    "motivational_messages": True
                },
                "schedule": {
                    "workout_time": "07:00",  # Padrão manhã
                    "meal_times": ["08:00", "12:00", "15:00", "19:00"],
                    "check_in_frequency": "weekly"
                },
                "timestamp": event_data["timestamp"]
            }
            
            response = await self.http_client.post(
                f"{notifications_service_url}/events/user-onboarded",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Service-Name": "users-service"
                }
            )
            
            if response.status_code == 200:
                logger.info("Serviço de notificações configurado", user_id=event_data["user_id"])
                return True
            else:
                logger.warning("Erro ao configurar notificações", status_code=response.status_code)
                return False
                
        except Exception as e:
            logger.error("Erro ao notificar serviço de notificações", error=str(e))
            return False
    
    async def _notify_analytics_service(self, event_data: Dict[str, Any]) -> bool:
        """Notificar serviço de analytics"""
        try:
            analytics_service_url = settings.analytics_service_url
            
            if not analytics_service_url:
                logger.info("URL do serviço de analytics não configurada")
                return False
            
            # Preparar dados para analytics
            payload = {
                "event_name": "user_onboarding_completed",
                "user_id": event_data["user_id"],
                "properties": {
                    "primary_goal": event_data["data"]["primary_goal"],
                    "training_experience": event_data["data"]["training_experience"],
                    "available_days": event_data["data"]["available_days"],
                    "bmr": event_data["data"]["bmr"],
                    "tdee": event_data["data"]["tdee"],
                    "maintenance_calories": event_data["data"]["maintenance_calories"]
                },
                "timestamp": event_data["timestamp"]
            }
            
            response = await self.http_client.post(
                f"{analytics_service_url}/events/track",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Service-Name": "users-service"
                }
            )
            
            if response.status_code == 200:
                logger.info("Evento enviado para analytics", user_id=event_data["user_id"])
                return True
            else:
                logger.warning("Erro ao enviar para analytics", status_code=response.status_code)
                return False
                
        except Exception as e:
            logger.error("Erro ao notificar analytics", error=str(e))
            return False
    
    async def _publish_to_pubsub(self, event_data: Dict[str, Any]) -> bool:
        """Publicar evento no Google Pub/Sub"""
        try:
            # Implementação simplificada - em produção usar biblioteca oficial
            pubsub_topic = settings.pubsub_topic
            
            if not pubsub_topic:
                logger.info("Tópico Pub/Sub não configurado")
                return False
            
            # Para implementação completa, usar google-cloud-pubsub
            # from google.cloud import pubsub_v1
            
            logger.info("Pub/Sub não implementado nesta versão")
            return False
            
        except Exception as e:
            logger.error("Erro ao publicar no Pub/Sub", error=str(e))
            return False
    
    async def notify_user_updated(
        self,
        user_id: str,
        update_type: str,
        updated_data: Dict[str, Any]
    ) -> bool:
        """Notificar que dados do usuário foram atualizados"""
        try:
            event_data = {
                "event_type": "user_updated",
                "user_id": user_id,
                "update_type": update_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": updated_data
            }
            
            # Salvar evento
            await self._save_event_to_firestore(event_data)
            
            # Notificar serviços relevantes baseado no tipo de atualização
            if update_type in ["fitness_goals", "calorie_calculation"]:
                await self._notify_plans_service(event_data)
            
            if update_type in ["preferences", "notifications_settings"]:
                await self._notify_notifications_service(event_data)
            
            # Sempre notificar analytics
            await self._notify_analytics_service(event_data)
            
            logger.info("Notificação de atualização enviada", user_id=user_id, update_type=update_type)
            return True
            
        except Exception as e:
            logger.error("Erro ao notificar atualização", error=str(e))
            return False
    
    async def notify_user_deactivated(self, user_id: str, reason: str) -> bool:
        """Notificar que usuário foi desativado"""
        try:
            event_data = {
                "event_type": "user_deactivated",
                "user_id": user_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Salvar evento
            await self._save_event_to_firestore(event_data)
            
            # Notificar todos os serviços para limpeza
            await self._notify_plans_service(event_data)
            await self._notify_notifications_service(event_data)
            await self._notify_analytics_service(event_data)
            
            logger.info("Notificação de desativação enviada", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao notificar desativação", error=str(e))
            return False
    
    async def health_check_services(self) -> Dict[str, bool]:
        """Verificar saúde dos serviços conectados"""
        try:
            services_status = {}
            
            # Verificar serviço de planos
            if settings.plans_service_url:
                try:
                    response = await self.http_client.get(
                        f"{settings.plans_service_url}/health",
                        timeout=5.0
                    )
                    services_status["plans_service"] = response.status_code == 200
                except:
                    services_status["plans_service"] = False
            else:
                services_status["plans_service"] = None
            
            # Verificar serviço de notificações
            if settings.notifications_service_url:
                try:
                    response = await self.http_client.get(
                        f"{settings.notifications_service_url}/health",
                        timeout=5.0
                    )
                    services_status["notifications_service"] = response.status_code == 200
                except:
                    services_status["notifications_service"] = False
            else:
                services_status["notifications_service"] = None
            
            # Verificar serviço de analytics
            if settings.analytics_service_url:
                try:
                    response = await self.http_client.get(
                        f"{settings.analytics_service_url}/health",
                        timeout=5.0
                    )
                    services_status["analytics_service"] = response.status_code == 200
                except:
                    services_status["analytics_service"] = False
            else:
                services_status["analytics_service"] = None
            
            return services_status
            
        except Exception as e:
            logger.error("Erro no health check dos serviços", error=str(e))
            return {}
    
    async def close(self):
        """Fechar conexões HTTP"""
        try:
            await self.http_client.aclose()
        except Exception as e:
            logger.error("Erro ao fechar cliente HTTP", error=str(e))


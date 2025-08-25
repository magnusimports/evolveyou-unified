"""
Serviço de gestão de usuários
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
import structlog

from config.settings import get_settings
from models.user import (
    UserProfile, OnboardingData, CalorieCalculation,
    HealthAssessment, MedicalHistory, LifestyleAssessment, 
    FitnessGoals, UserPreferences
)
from services.firebase_service import FirebaseService

logger = structlog.get_logger()
settings = get_settings()

class UserService:
    """Serviço para gestão de usuários"""
    
    def __init__(self, firebase_service: FirebaseService):
        self.firebase_service = firebase_service
    
    async def email_exists(self, email: str) -> bool:
        """Verificar se email já existe"""
        try:
            user = await self.firebase_service.get_user_by_email(email)
            return user is not None
        except Exception as e:
            logger.error("Erro ao verificar email", error=str(e))
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Buscar usuário por ID"""
        try:
            user_data = await self.firebase_service.get_user_by_id(user_id)
            
            if not user_data:
                return None
            
            # Converter data de nascimento se necessário
            if isinstance(user_data.get("date_of_birth"), str):
                user_data["date_of_birth"] = datetime.fromisoformat(user_data["date_of_birth"]).date()
            
            return UserProfile(**user_data)
            
        except Exception as e:
            logger.error("Erro ao buscar usuário", error=str(e))
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Buscar usuário por email"""
        try:
            user_data = await self.firebase_service.get_user_by_email(email)
            
            if not user_data:
                return None
            
            # Converter data de nascimento se necessário
            if isinstance(user_data.get("date_of_birth"), str):
                user_data["date_of_birth"] = datetime.fromisoformat(user_data["date_of_birth"]).date()
            
            return UserProfile(**user_data)
            
        except Exception as e:
            logger.error("Erro ao buscar usuário por email", error=str(e))
            raise
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Atualizar perfil do usuário"""
        try:
            # Adicionar timestamp de atualização
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            await self.firebase_service.update_user(user_id, updates)
            
            logger.info("Perfil atualizado", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar perfil", error=str(e))
            raise
    
    async def validate_onboarding_data(self, onboarding_data: OnboardingData) -> bool:
        """Validar dados do onboarding"""
        try:
            # Validações específicas de negócio
            health = onboarding_data.health_assessment
            
            # Validar IMC
            height_m = health.height / 100
            bmi = health.weight / (height_m ** 2)
            
            if bmi < 10 or bmi > 60:
                raise ValueError(f"IMC calculado ({bmi:.1f}) está fora do range válido")
            
            # Validar pressão arterial se fornecida
            if health.systolic_pressure and health.diastolic_pressure:
                if health.systolic_pressure <= health.diastolic_pressure:
                    raise ValueError("Pressão sistólica deve ser maior que diastólica")
            
            # Validar frequência cardíaca
            if health.resting_heart_rate and health.max_heart_rate:
                if health.resting_heart_rate >= health.max_heart_rate:
                    raise ValueError("FC de repouso deve ser menor que FC máxima")
            
            # Validar metas de peso
            goals = onboarding_data.fitness_goals
            if goals.target_weight:
                weight_diff = abs(goals.target_weight - health.weight)
                if weight_diff > health.weight * 0.5:  # Mais de 50% do peso atual
                    raise ValueError("Meta de peso muito extrema")
            
            # Validar timeline
            if goals.timeline_weeks > 104:  # 2 anos
                raise ValueError("Timeline muito longo (máximo 2 anos)")
            
            logger.info("Dados de onboarding validados com sucesso")
            return True
            
        except Exception as e:
            logger.error("Erro na validação do onboarding", error=str(e))
            raise
    
    async def complete_onboarding(
        self, 
        user_id: str, 
        onboarding_data: OnboardingData,
        calorie_calculation: CalorieCalculation
    ) -> bool:
        """Completar onboarding do usuário"""
        try:
            # Preparar dados para salvar
            onboarding_dict = onboarding_data.dict()
            onboarding_dict["completed_at"] = datetime.utcnow().isoformat()
            
            # Atualizar perfil do usuário
            updates = {
                "onboarding_completed": True,
                "onboarding_data": onboarding_dict,
                "calorie_calculation": calorie_calculation.dict(),
                "updated_at": datetime.utcnow().isoformat(),
                # Atualizar dados básicos se necessário
                "height": onboarding_data.health_assessment.height,
                "weight": onboarding_data.health_assessment.weight,
                "fitness_goals": onboarding_data.fitness_goals.dict(),
                "preferences": onboarding_data.preferences.dict()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            # Registrar evento
            await self.firebase_service.log_auth_event(
                user_id,
                "onboarding_completed",
                {
                    "primary_goal": onboarding_data.fitness_goals.primary_goal,
                    "bmr": calorie_calculation.bmr,
                    "tdee": calorie_calculation.tdee
                }
            )
            
            logger.info("Onboarding concluído", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao completar onboarding", error=str(e))
            raise
    
    async def update_calorie_calculation(
        self, 
        user_id: str, 
        calorie_calculation: CalorieCalculation
    ) -> bool:
        """Atualizar cálculo calórico do usuário"""
        try:
            updates = {
                "calorie_calculation": calorie_calculation.dict(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            logger.info("Cálculo calórico atualizado", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar cálculo calórico", error=str(e))
            raise
    
    async def update_health_data(
        self, 
        user_id: str, 
        health_data: HealthAssessment
    ) -> bool:
        """Atualizar dados de saúde"""
        try:
            # Buscar usuário atual
            user = await self.get_user_by_id(user_id)
            
            if not user or not user.onboarding_data:
                raise ValueError("Usuário não encontrado ou onboarding não concluído")
            
            # Atualizar dados de saúde no onboarding
            onboarding_data = user.onboarding_data.dict()
            onboarding_data["health_assessment"] = health_data.dict()
            
            updates = {
                "onboarding_data": onboarding_data,
                "height": health_data.height,
                "weight": health_data.weight,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            logger.info("Dados de saúde atualizados", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar dados de saúde", error=str(e))
            raise
    
    async def update_fitness_goals(
        self, 
        user_id: str, 
        fitness_goals: FitnessGoals
    ) -> bool:
        """Atualizar objetivos fitness"""
        try:
            # Buscar usuário atual
            user = await self.get_user_by_id(user_id)
            
            if not user or not user.onboarding_data:
                raise ValueError("Usuário não encontrado ou onboarding não concluído")
            
            # Atualizar objetivos no onboarding
            onboarding_data = user.onboarding_data.dict()
            onboarding_data["fitness_goals"] = fitness_goals.dict()
            
            updates = {
                "onboarding_data": onboarding_data,
                "fitness_goals": fitness_goals.dict(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            logger.info("Objetivos fitness atualizados", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar objetivos fitness", error=str(e))
            raise
    
    async def update_preferences(
        self, 
        user_id: str, 
        preferences: UserPreferences
    ) -> bool:
        """Atualizar preferências do usuário"""
        try:
            updates = {
                "preferences": preferences.dict(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            logger.info("Preferências atualizadas", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar preferências", error=str(e))
            raise
    
    async def upload_profile_picture(self, user_id: str, image_url: str) -> bool:
        """Atualizar foto de perfil"""
        try:
            updates = {
                "profile_picture": image_url,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            logger.info("Foto de perfil atualizada", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar foto de perfil", error=str(e))
            raise
    
    async def add_progress_photo(self, user_id: str, photo_url: str) -> bool:
        """Adicionar foto de progresso"""
        try:
            # Buscar usuário atual
            user = await self.get_user_by_id(user_id)
            
            if not user:
                raise ValueError("Usuário não encontrado")
            
            # Adicionar nova foto à lista
            progress_photos = user.progress_photos or []
            progress_photos.append(photo_url)
            
            updates = {
                "progress_photos": progress_photos,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            logger.info("Foto de progresso adicionada", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao adicionar foto de progresso", error=str(e))
            raise
    
    async def deactivate_user(self, user_id: str, reason: str = "user_request") -> bool:
        """Desativar usuário"""
        try:
            updates = {
                "is_active": False,
                "deactivated_at": datetime.utcnow().isoformat(),
                "deactivation_reason": reason,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            # Registrar evento
            await self.firebase_service.log_auth_event(
                user_id,
                "user_deactivated",
                {"reason": reason}
            )
            
            logger.info("Usuário desativado", user_id=user_id, reason=reason)
            return True
            
        except Exception as e:
            logger.error("Erro ao desativar usuário", error=str(e))
            raise
    
    async def reactivate_user(self, user_id: str) -> bool:
        """Reativar usuário"""
        try:
            updates = {
                "is_active": True,
                "reactivated_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            # Registrar evento
            await self.firebase_service.log_auth_event(
                user_id,
                "user_reactivated",
                {}
            )
            
            logger.info("Usuário reativado", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao reativar usuário", error=str(e))
            raise
    
    async def verify_email(self, user_id: str) -> bool:
        """Marcar email como verificado"""
        try:
            updates = {
                "is_verified": True,
                "email_verified_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            # Registrar evento
            await self.firebase_service.log_auth_event(
                user_id,
                "email_verified",
                {}
            )
            
            logger.info("Email verificado", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao verificar email", error=str(e))
            raise
    
    async def upgrade_to_premium(self, user_id: str, subscription_data: Dict[str, Any]) -> bool:
        """Atualizar usuário para premium"""
        try:
            updates = {
                "is_premium": True,
                "premium_since": datetime.utcnow().isoformat(),
                "subscription_data": subscription_data,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.firebase_service.update_user(user_id, updates)
            
            # Registrar evento
            await self.firebase_service.log_auth_event(
                user_id,
                "upgraded_to_premium",
                subscription_data
            )
            
            logger.info("Usuário atualizado para premium", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar para premium", error=str(e))
            raise
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Obter estatísticas do usuário"""
        try:
            user = await self.get_user_by_id(user_id)
            
            if not user:
                raise ValueError("Usuário não encontrado")
            
            # Calcular estatísticas básicas
            stats = {
                "account_age_days": (datetime.utcnow().date() - user.created_at.date()).days,
                "onboarding_completed": user.onboarding_completed,
                "is_premium": user.is_premium,
                "is_verified": user.is_verified,
                "progress_photos_count": len(user.progress_photos or []),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            
            # Adicionar estatísticas de onboarding se disponível
            if user.onboarding_data:
                health = user.onboarding_data.health_assessment
                height_m = health.height / 100
                bmi = health.weight / (height_m ** 2)
                
                stats.update({
                    "current_weight": health.weight,
                    "current_height": health.height,
                    "bmi": round(bmi, 1),
                    "primary_goal": user.onboarding_data.fitness_goals.primary_goal
                })
                
                # Adicionar dados calóricos se disponível
                if user.calorie_calculation:
                    stats.update({
                        "bmr": user.calorie_calculation.bmr,
                        "tdee": user.calorie_calculation.tdee,
                        "maintenance_calories": user.calorie_calculation.maintenance_calories
                    })
            
            return stats
            
        except Exception as e:
            logger.error("Erro ao obter estatísticas", error=str(e))
            raise


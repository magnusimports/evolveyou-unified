"""
Serviço de autenticação e JWT
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
import httpx
import structlog

from config.settings import get_settings
from models.user import UserRegistration, SocialLogin, UserProfile, AuthTokens
from services.firebase_service import FirebaseService

logger = structlog.get_logger()
settings = get_settings()

class AuthService:
    """Serviço de autenticação"""
    
    def __init__(self, firebase_service: FirebaseService):
        self.firebase_service = firebase_service
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    def hash_password(self, password: str) -> str:
        """Criptografar senha"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar senha"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_jwt_token(self, user_id: str, token_type: str = "access") -> str:
        """Gerar token JWT"""
        now = datetime.utcnow()
        
        if token_type == "access":
            expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        else:  # refresh
            expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "type": token_type,
            "iat": now,
            "exp": expire,
            "iss": "evolveyou-users-service"
        }
        
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verificar token JWT"""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expirado")
        except jwt.InvalidTokenError:
            raise ValueError("Token inválido")
    
    async def register_user(self, user_data: UserRegistration) -> UserProfile:
        """Registrar novo usuário"""
        try:
            # Criptografar senha
            hashed_password = self.hash_password(user_data.password)
            
            # Preparar dados do usuário
            user_dict = {
                "email": user_data.email,
                "password_hash": hashed_password,
                "name": user_data.name,
                "date_of_birth": user_data.date_of_birth.isoformat(),
                "gender": user_data.gender,
                "is_active": True,
                "is_verified": False,
                "is_premium": False,
                "onboarding_completed": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "terms_accepted": user_data.terms_accepted,
                "privacy_accepted": user_data.privacy_accepted,
                "marketing_consent": user_data.marketing_consent
            }
            
            # Criar usuário no Firestore
            user_id = await self.firebase_service.create_user(user_dict)
            
            # Criar usuário no Firebase Auth (opcional, para compatibilidade)
            try:
                firebase_uid = await self.firebase_service.create_firebase_user(
                    user_data.email,
                    user_data.password,
                    user_data.name
                )
                # Atualizar com Firebase UID
                await self.firebase_service.update_user(user_id, {"firebase_uid": firebase_uid})
            except Exception as e:
                logger.warning("Erro ao criar usuário no Firebase Auth", error=str(e))
            
            # Registrar evento de registro
            await self.firebase_service.log_auth_event(
                user_id,
                "user_registered",
                {"email": user_data.email, "method": "email_password"}
            )
            
            # Retornar perfil do usuário
            user_dict["id"] = user_id
            user_dict["date_of_birth"] = user_data.date_of_birth
            
            return UserProfile(**user_dict)
            
        except Exception as e:
            logger.error("Erro no registro de usuário", error=str(e))
            raise
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserProfile]:
        """Autenticar usuário com email e senha"""
        try:
            # Buscar usuário por email
            user_data = await self.firebase_service.get_user_by_email(email)
            
            if not user_data:
                return None
            
            # Verificar se usuário está ativo
            if not user_data.get("is_active", True):
                return None
            
            # Verificar senha
            if not self.verify_password(password, user_data.get("password_hash", "")):
                return None
            
            # Registrar evento de login
            await self.firebase_service.log_auth_event(
                user_data["id"],
                "user_login",
                {"email": email, "method": "email_password"}
            )
            
            # Converter data de nascimento
            if isinstance(user_data["date_of_birth"], str):
                user_data["date_of_birth"] = datetime.fromisoformat(user_data["date_of_birth"]).date()
            
            return UserProfile(**user_data)
            
        except Exception as e:
            logger.error("Erro na autenticação", error=str(e))
            raise
    
    async def generate_tokens(self, user_id: str) -> AuthTokens:
        """Gerar tokens de acesso e refresh"""
        try:
            access_token = self.generate_jwt_token(user_id, "access")
            refresh_token = self.generate_jwt_token(user_id, "refresh")
            
            # Salvar refresh token no banco
            expires_at = int((datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)).timestamp())
            await self.firebase_service.save_refresh_token(user_id, refresh_token, expires_at)
            
            return AuthTokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.jwt_access_token_expire_minutes * 60
            )
            
        except Exception as e:
            logger.error("Erro ao gerar tokens", error=str(e))
            raise
    
    async def refresh_tokens(self, refresh_token: str) -> AuthTokens:
        """Renovar tokens usando refresh token"""
        try:
            # Verificar token
            payload = self.verify_jwt_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise ValueError("Token inválido")
            
            user_id = payload.get("sub")
            
            # Verificar se refresh token existe no banco
            token_data = await self.firebase_service.get_refresh_token(refresh_token)
            
            if not token_data or token_data["user_id"] != user_id:
                raise ValueError("Refresh token inválido")
            
            # Revogar token antigo
            await self.firebase_service.revoke_refresh_token(refresh_token)
            
            # Gerar novos tokens
            return await self.generate_tokens(user_id)
            
        except Exception as e:
            logger.error("Erro ao renovar tokens", error=str(e))
            raise
    
    async def verify_social_token(self, social_data: SocialLogin) -> Dict[str, Any]:
        """Verificar token de provedor social"""
        try:
            if social_data.provider == "google":
                return await self._verify_google_token(social_data.token)
            elif social_data.provider == "apple":
                return await self._verify_apple_token(social_data.token)
            elif social_data.provider == "facebook":
                return await self._verify_facebook_token(social_data.token)
            else:
                raise ValueError(f"Provedor não suportado: {social_data.provider}")
                
        except Exception as e:
            logger.error("Erro ao verificar token social", error=str(e))
            raise
    
    async def _verify_google_token(self, token: str) -> Dict[str, Any]:
        """Verificar token do Google"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}"
                )
                
                if response.status_code != 200:
                    raise ValueError("Token Google inválido")
                
                data = response.json()
                
                return {
                    "provider": "google",
                    "provider_id": data.get("user_id"),
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "verified_email": data.get("verified_email", False)
                }
                
        except Exception as e:
            logger.error("Erro ao verificar token Google", error=str(e))
            raise
    
    async def _verify_apple_token(self, token: str) -> Dict[str, Any]:
        """Verificar token da Apple"""
        # Implementação simplificada - em produção usar biblioteca específica
        try:
            # Decodificar JWT da Apple (sem verificação de assinatura para exemplo)
            import base64
            import json
            
            # Dividir token JWT
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Token Apple inválido")
            
            # Decodificar payload
            payload = parts[1]
            # Adicionar padding se necessário
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.b64decode(payload)
            data = json.loads(decoded)
            
            return {
                "provider": "apple",
                "provider_id": data.get("sub"),
                "email": data.get("email"),
                "name": data.get("name"),
                "verified_email": data.get("email_verified", False)
            }
            
        except Exception as e:
            logger.error("Erro ao verificar token Apple", error=str(e))
            raise
    
    async def _verify_facebook_token(self, token: str) -> Dict[str, Any]:
        """Verificar token do Facebook"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://graph.facebook.com/me?access_token={token}&fields=id,name,email"
                )
                
                if response.status_code != 200:
                    raise ValueError("Token Facebook inválido")
                
                data = response.json()
                
                return {
                    "provider": "facebook",
                    "provider_id": data.get("id"),
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "verified_email": True  # Facebook sempre verifica email
                }
                
        except Exception as e:
            logger.error("Erro ao verificar token Facebook", error=str(e))
            raise
    
    async def get_or_create_social_user(self, user_info: Dict[str, Any]) -> UserProfile:
        """Buscar ou criar usuário a partir de login social"""
        try:
            email = user_info.get("email")
            
            if not email:
                raise ValueError("Email é obrigatório para login social")
            
            # Buscar usuário existente
            existing_user = await self.firebase_service.get_user_by_email(email)
            
            if existing_user:
                # Atualizar informações do provedor social
                social_providers = existing_user.get("social_providers", {})
                social_providers[user_info["provider"]] = {
                    "provider_id": user_info["provider_id"],
                    "connected_at": datetime.utcnow().isoformat()
                }
                
                await self.firebase_service.update_user(
                    existing_user["id"],
                    {
                        "social_providers": social_providers,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                )
                
                # Converter data de nascimento se necessário
                if isinstance(existing_user["date_of_birth"], str):
                    existing_user["date_of_birth"] = datetime.fromisoformat(existing_user["date_of_birth"]).date()
                
                return UserProfile(**existing_user)
            
            else:
                # Criar novo usuário
                user_dict = {
                    "email": email,
                    "name": user_info.get("name", ""),
                    "date_of_birth": "1990-01-01",  # Padrão - será atualizado no onboarding
                    "gender": "prefer_not_to_say",  # Padrão
                    "is_active": True,
                    "is_verified": user_info.get("verified_email", False),
                    "is_premium": False,
                    "onboarding_completed": False,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "social_providers": {
                        user_info["provider"]: {
                            "provider_id": user_info["provider_id"],
                            "connected_at": datetime.utcnow().isoformat()
                        }
                    },
                    "registration_method": "social_login"
                }
                
                # Criar usuário
                user_id = await self.firebase_service.create_user(user_dict)
                
                # Registrar evento
                await self.firebase_service.log_auth_event(
                    user_id,
                    "user_registered",
                    {"email": email, "method": "social_login", "provider": user_info["provider"]}
                )
                
                user_dict["id"] = user_id
                user_dict["date_of_birth"] = datetime.fromisoformat(user_dict["date_of_birth"]).date()
                
                return UserProfile(**user_dict)
                
        except Exception as e:
            logger.error("Erro ao processar usuário social", error=str(e))
            raise
    
    async def update_last_login(self, user_id: str) -> bool:
        """Atualizar último login do usuário"""
        try:
            await self.firebase_service.update_user(
                user_id,
                {
                    "last_login": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar último login", error=str(e))
            raise
    
    async def logout_user(self, user_id: str, refresh_token: str) -> bool:
        """Fazer logout do usuário"""
        try:
            # Revogar refresh token
            await self.firebase_service.revoke_refresh_token(refresh_token)
            
            # Registrar evento
            await self.firebase_service.log_auth_event(
                user_id,
                "user_logout",
                {"method": "manual"}
            )
            
            return True
            
        except Exception as e:
            logger.error("Erro no logout", error=str(e))
            raise
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Alterar senha do usuário"""
        try:
            # Buscar usuário
            user_data = await self.firebase_service.get_user_by_id(user_id)
            
            if not user_data:
                raise ValueError("Usuário não encontrado")
            
            # Verificar senha atual
            if not self.verify_password(old_password, user_data.get("password_hash", "")):
                raise ValueError("Senha atual incorreta")
            
            # Criptografar nova senha
            new_password_hash = self.hash_password(new_password)
            
            # Atualizar no banco
            await self.firebase_service.update_user(
                user_id,
                {
                    "password_hash": new_password_hash,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            # Registrar evento
            await self.firebase_service.log_auth_event(
                user_id,
                "password_changed",
                {"method": "user_request"}
            )
            
            return True
            
        except Exception as e:
            logger.error("Erro ao alterar senha", error=str(e))
            raise


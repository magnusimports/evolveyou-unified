"""
Middleware de autenticação
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import structlog

from config.settings import get_settings
from services.firebase_service import FirebaseService

logger = structlog.get_logger()
settings = get_settings()

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verificar token JWT"""
    try:
        token = credentials.credentials
        
        # Decodificar token
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Verificar tipo do token
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido"
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    except Exception as e:
        logger.error("Erro na verificação do token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na autenticação"
        )

async def get_current_user(token_payload: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """Obter usuário atual a partir do token"""
    try:
        user_id = token_payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Buscar usuário no banco (usando o app state)
        from main import app
        firebase_service: FirebaseService = app.state.firebase_service
        
        user_data = await firebase_service.get_user_by_id(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        if not user_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo"
            )
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar usuário atual", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Requerer privilégios de administrador"""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado - privilégios de administrador necessários"
        )
    
    return current_user

async def require_premium(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Requerer assinatura premium"""
    if not current_user.get("is_premium", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado - assinatura premium necessária"
        )
    
    return current_user

async def require_verified(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Requerer email verificado"""
    if not current_user.get("is_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado - email não verificado"
        )
    
    return current_user

async def require_onboarding(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Requerer onboarding completo"""
    if not current_user.get("onboarding_completed", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado - onboarding não concluído"
        )
    
    return current_user

class OptionalAuth:
    """Autenticação opcional - não falha se não houver token"""
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
    
    async def __call__(self, credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[Dict[str, Any]]:
        if not credentials:
            return None
        
        try:
            return await verify_token(credentials)
        except HTTPException:
            return None

optional_auth = OptionalAuth()

async def get_current_user_optional(token_payload: Optional[Dict[str, Any]] = Depends(optional_auth)) -> Optional[Dict[str, Any]]:
    """Obter usuário atual (opcional)"""
    if not token_payload:
        return None
    
    try:
        user_id = token_payload.get("sub")
        
        if not user_id:
            return None
        
        # Buscar usuário no banco
        from main import app
        firebase_service: FirebaseService = app.state.firebase_service
        
        user_data = await firebase_service.get_user_by_id(user_id)
        
        if not user_data or not user_data.get("is_active", True):
            return None
        
        return user_data
        
    except Exception as e:
        logger.error("Erro na autenticação opcional", error=str(e))
        return None


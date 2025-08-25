"""
Middleware de autenticação Firebase
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth
import structlog
from typing import Optional

logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)

async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Verificar token Firebase (opcional para endpoints públicos)
    """
    if not credentials:
        return None
    
    try:
        # Verificar token Firebase
        decoded_token = auth.verify_id_token(credentials.credentials)
        
        logger.info("Token verificado", uid=decoded_token.get("uid"))
        return decoded_token
        
    except Exception as e:
        logger.warning("Token inválido", error=str(e))
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação inválido"
        )

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Exigir autenticação (para endpoints protegidos)
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação necessário"
        )
    
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        logger.info("Acesso autorizado", uid=decoded_token.get("uid"))
        return decoded_token
        
    except Exception as e:
        logger.warning("Falha na autenticação", error=str(e))
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação inválido"
        )


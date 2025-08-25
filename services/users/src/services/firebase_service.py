"""
Serviço de integração com Firebase
"""

import os
import json
from typing import Optional, Dict, Any, List
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

class FirebaseService:
    """Serviço para interação com Firebase"""
    
    def __init__(self):
        self.app = None
        self.db = None
        self.auth = None
        
    async def initialize(self):
        """Inicializar conexão com Firebase"""
        try:
            if not firebase_admin._apps:
                # Configurar credenciais
                if settings.firebase_credentials_path and os.path.exists(settings.firebase_credentials_path):
                    cred = credentials.Certificate(settings.firebase_credentials_path)
                else:
                    # Usar credenciais padrão do ambiente
                    cred = credentials.ApplicationDefault()
                
                # Inicializar app
                self.app = firebase_admin.initialize_app(cred, {
                    'projectId': settings.firebase_project_id
                })
            else:
                self.app = firebase_admin.get_app()
            
            # Inicializar serviços
            self.db = firestore.client()
            self.auth = auth
            
            logger.info("Firebase inicializado com sucesso", project_id=settings.firebase_project_id)
            
        except Exception as e:
            logger.error("Erro ao inicializar Firebase", error=str(e))
            raise
    
    # Métodos para usuários
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Criar usuário no Firestore"""
        try:
            doc_ref = self.db.collection('users').document()
            user_data['id'] = doc_ref.id
            doc_ref.set(user_data)
            
            logger.info("Usuário criado no Firestore", user_id=doc_ref.id)
            return doc_ref.id
            
        except Exception as e:
            logger.error("Erro ao criar usuário", error=str(e))
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Buscar usuário por ID"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error("Erro ao buscar usuário", error=str(e), user_id=user_id)
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Buscar usuário por email"""
        try:
            query = self.db.collection('users').where(
                filter=FieldFilter('email', '==', email)
            ).limit(1)
            
            docs = query.get()
            
            if docs:
                return docs[0].to_dict()
            return None
            
        except Exception as e:
            logger.error("Erro ao buscar usuário por email", error=str(e), email=email)
            raise
    
    async def update_user(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Atualizar dados do usuário"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.update(data)
            
            logger.info("Usuário atualizado", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar usuário", error=str(e), user_id=user_id)
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Deletar usuário (soft delete)"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.update({
                'is_active': False,
                'deleted_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info("Usuário deletado", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao deletar usuário", error=str(e), user_id=user_id)
            raise
    
    # Métodos para autenticação
    async def create_firebase_user(self, email: str, password: str, name: str) -> str:
        """Criar usuário no Firebase Auth"""
        try:
            user_record = self.auth.create_user(
                email=email,
                password=password,
                display_name=name,
                email_verified=False
            )
            
            logger.info("Usuário criado no Firebase Auth", uid=user_record.uid)
            return user_record.uid
            
        except Exception as e:
            logger.error("Erro ao criar usuário no Firebase Auth", error=str(e))
            raise
    
    async def verify_firebase_token(self, token: str) -> Dict[str, Any]:
        """Verificar token do Firebase"""
        try:
            decoded_token = self.auth.verify_id_token(token)
            return decoded_token
            
        except Exception as e:
            logger.error("Erro ao verificar token Firebase", error=str(e))
            raise
    
    async def get_firebase_user(self, uid: str) -> Dict[str, Any]:
        """Obter usuário do Firebase Auth"""
        try:
            user_record = self.auth.get_user(uid)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'email_verified': user_record.email_verified,
                'provider_data': [
                    {
                        'provider_id': provider.provider_id,
                        'uid': provider.uid,
                        'email': provider.email
                    }
                    for provider in user_record.provider_data
                ]
            }
            
        except Exception as e:
            logger.error("Erro ao buscar usuário Firebase", error=str(e), uid=uid)
            raise
    
    async def update_firebase_user(self, uid: str, **kwargs) -> bool:
        """Atualizar usuário no Firebase Auth"""
        try:
            self.auth.update_user(uid, **kwargs)
            logger.info("Usuário Firebase atualizado", uid=uid)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar usuário Firebase", error=str(e), uid=uid)
            raise
    
    # Métodos para tokens de refresh
    async def save_refresh_token(self, user_id: str, token: str, expires_at: int) -> bool:
        """Salvar refresh token"""
        try:
            doc_ref = self.db.collection('refresh_tokens').document()
            doc_ref.set({
                'user_id': user_id,
                'token': token,
                'expires_at': expires_at,
                'created_at': firestore.SERVER_TIMESTAMP,
                'is_active': True
            })
            
            return True
            
        except Exception as e:
            logger.error("Erro ao salvar refresh token", error=str(e))
            raise
    
    async def get_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Buscar refresh token"""
        try:
            query = self.db.collection('refresh_tokens').where(
                filter=FieldFilter('token', '==', token)
            ).where(
                filter=FieldFilter('is_active', '==', True)
            ).limit(1)
            
            docs = query.get()
            
            if docs:
                return docs[0].to_dict()
            return None
            
        except Exception as e:
            logger.error("Erro ao buscar refresh token", error=str(e))
            raise
    
    async def revoke_refresh_token(self, token: str) -> bool:
        """Revogar refresh token"""
        try:
            query = self.db.collection('refresh_tokens').where(
                filter=FieldFilter('token', '==', token)
            )
            
            docs = query.get()
            
            for doc in docs:
                doc.reference.update({'is_active': False})
            
            return True
            
        except Exception as e:
            logger.error("Erro ao revogar refresh token", error=str(e))
            raise
    
    # Métodos para sessões
    async def create_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Criar sessão de usuário"""
        try:
            doc_ref = self.db.collection('user_sessions').document()
            session_data.update({
                'id': doc_ref.id,
                'user_id': user_id,
                'created_at': firestore.SERVER_TIMESTAMP,
                'is_active': True
            })
            doc_ref.set(session_data)
            
            return doc_ref.id
            
        except Exception as e:
            logger.error("Erro ao criar sessão", error=str(e))
            raise
    
    async def get_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Buscar sessões ativas do usuário"""
        try:
            query = self.db.collection('user_sessions').where(
                filter=FieldFilter('user_id', '==', user_id)
            ).where(
                filter=FieldFilter('is_active', '==', True)
            )
            
            docs = query.get()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            logger.error("Erro ao buscar sessões", error=str(e))
            raise
    
    async def end_session(self, session_id: str) -> bool:
        """Finalizar sessão"""
        try:
            doc_ref = self.db.collection('user_sessions').document(session_id)
            doc_ref.update({
                'is_active': False,
                'ended_at': firestore.SERVER_TIMESTAMP
            })
            
            return True
            
        except Exception as e:
            logger.error("Erro ao finalizar sessão", error=str(e))
            raise
    
    # Métodos para logs de auditoria
    async def log_auth_event(self, user_id: str, event_type: str, details: Dict[str, Any]) -> bool:
        """Registrar evento de autenticação"""
        try:
            doc_ref = self.db.collection('auth_logs').document()
            doc_ref.set({
                'user_id': user_id,
                'event_type': event_type,
                'details': details,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'ip_address': details.get('ip_address'),
                'user_agent': details.get('user_agent')
            })
            
            return True
            
        except Exception as e:
            logger.error("Erro ao registrar log de auth", error=str(e))
            raise
    
    # Métodos para verificação de email
    async def create_email_verification(self, user_id: str, token: str) -> bool:
        """Criar token de verificação de email"""
        try:
            doc_ref = self.db.collection('email_verifications').document()
            doc_ref.set({
                'user_id': user_id,
                'token': token,
                'created_at': firestore.SERVER_TIMESTAMP,
                'expires_at': firestore.SERVER_TIMESTAMP,  # + 24 horas
                'is_used': False
            })
            
            return True
            
        except Exception as e:
            logger.error("Erro ao criar verificação de email", error=str(e))
            raise
    
    async def verify_email_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verificar token de email"""
        try:
            query = self.db.collection('email_verifications').where(
                filter=FieldFilter('token', '==', token)
            ).where(
                filter=FieldFilter('is_used', '==', False)
            ).limit(1)
            
            docs = query.get()
            
            if docs:
                doc = docs[0]
                # Marcar como usado
                doc.reference.update({'is_used': True})
                return doc.to_dict()
            
            return None
            
        except Exception as e:
            logger.error("Erro ao verificar token de email", error=str(e))
            raise


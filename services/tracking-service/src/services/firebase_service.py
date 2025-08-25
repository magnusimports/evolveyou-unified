"""
Serviço de integração com Firebase/Firestore
"""

import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import structlog

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client, DocumentReference, CollectionReference

from config.settings import get_settings

logger = structlog.get_logger(__name__)


class FirebaseService:
    """Serviço para interação com Firebase/Firestore"""
    
    def __init__(self):
        self.db: Optional[Client] = None
        self.app: Optional[firebase_admin.App] = None
        self.settings = get_settings()
        
    async def initialize(self):
        """Inicializa a conexão com Firebase"""
        try:
            # Verificar se já foi inicializado
            if self.app is not None:
                logger.info("Firebase já inicializado")
                return
            
            # Configurar credenciais
            cred = None
            
            if self.settings.firebase_credentials_path and os.path.exists(self.settings.firebase_credentials_path):
                # Usar arquivo de credenciais
                cred = credentials.Certificate(self.settings.firebase_credentials_path)
                logger.info("Usando credenciais do arquivo", path=self.settings.firebase_credentials_path)
            else:
                # Usar credenciais padrão do ambiente (para Cloud Run)
                try:
                    cred = credentials.ApplicationDefault()
                    logger.info("Usando credenciais padrão da aplicação")
                except Exception as e:
                    logger.warning("Credenciais padrão não disponíveis", error=str(e))
                    # Fallback para desenvolvimento
                    if self.settings.environment == "development":
                        logger.info("Modo desenvolvimento - usando credenciais mock")
                        # Em desenvolvimento, pode usar emulador ou credenciais mock
                        pass
                    else:
                        raise
            
            # Inicializar Firebase Admin
            if cred:
                self.app = firebase_admin.initialize_app(cred, {
                    'projectId': self.settings.firebase_project_id
                })
            else:
                # Para desenvolvimento sem credenciais
                self.app = firebase_admin.initialize_app(options={
                    'projectId': self.settings.firebase_project_id
                })
            
            # Obter cliente Firestore
            self.db = firestore.client(app=self.app)
            
            logger.info("Firebase inicializado com sucesso", 
                       project_id=self.settings.firebase_project_id)
            
        except Exception as e:
            logger.error("Erro ao inicializar Firebase", error=str(e))
            raise
    
    async def close(self):
        """Fecha a conexão com Firebase"""
        try:
            if self.app:
                firebase_admin.delete_app(self.app)
                self.app = None
                self.db = None
                logger.info("Firebase finalizado")
        except Exception as e:
            logger.error("Erro ao finalizar Firebase", error=str(e))
    
    async def health_check(self) -> bool:
        """Verifica se a conexão com Firebase está saudável"""
        try:
            if not self.db:
                return False
            
            # Fazer uma query simples para testar conectividade
            test_ref = self.db.collection('_health_check').limit(1)
            list(test_ref.stream())
            
            return True
        except Exception as e:
            logger.error("Health check Firebase falhou", error=str(e))
            return False
    
    # Métodos para Daily Logs
    
    async def save_daily_log(self, log_data: Dict[str, Any]) -> str:
        """
        Salva um log diário no Firestore
        
        Args:
            log_data: Dados do log
            
        Returns:
            str: ID do documento criado
        """
        try:
            # Preparar dados para salvamento
            save_data = log_data.copy()
            
            # Converter datetime e date para timestamp
            if 'timestamp' in save_data and isinstance(save_data['timestamp'], datetime):
                save_data['timestamp'] = save_data['timestamp']
            
            if 'date' in save_data and isinstance(save_data['date'], date):
                save_data['date'] = save_data['date'].isoformat()
            
            # Adicionar metadados
            save_data['created_at'] = datetime.utcnow()
            save_data['updated_at'] = datetime.utcnow()
            
            # Salvar no Firestore
            doc_ref = self.db.collection('daily_logs').document()
            doc_ref.set(save_data)
            
            logger.info("Log salvo com sucesso", 
                       log_id=doc_ref.id,
                       user_id=log_data.get('user_id'),
                       log_type=log_data.get('log_type'))
            
            return doc_ref.id
            
        except Exception as e:
            logger.error("Erro ao salvar log", error=str(e), log_data=log_data)
            raise
    
    async def get_daily_logs(
        self, 
        user_id: str, 
        target_date: date,
        log_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém logs diários de um usuário para uma data específica
        
        Args:
            user_id: ID do usuário
            target_date: Data alvo
            log_types: Tipos de log a filtrar (opcional)
            
        Returns:
            List[Dict]: Lista de logs
        """
        try:
            # Construir query
            query = (self.db.collection('daily_logs')
                    .where('user_id', '==', user_id)
                    .where('date', '==', target_date.isoformat()))
            
            # Filtrar por tipos se especificado
            if log_types:
                query = query.where('log_type', 'in', log_types)
            
            # Ordenar por timestamp
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            # Executar query
            docs = query.stream()
            
            logs = []
            for doc in docs:
                log_data = doc.to_dict()
                log_data['log_id'] = doc.id
                logs.append(log_data)
            
            logger.info("Logs obtidos com sucesso", 
                       user_id=user_id,
                       date=target_date.isoformat(),
                       count=len(logs))
            
            return logs
            
        except Exception as e:
            logger.error("Erro ao obter logs", 
                        error=str(e),
                        user_id=user_id,
                        date=target_date.isoformat())
            raise
    
    async def get_logs_by_date_range(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        log_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém logs de um usuário em um período
        
        Args:
            user_id: ID do usuário
            start_date: Data inicial
            end_date: Data final
            log_types: Tipos de log a filtrar (opcional)
            
        Returns:
            List[Dict]: Lista de logs
        """
        try:
            # Construir query
            query = (self.db.collection('daily_logs')
                    .where('user_id', '==', user_id)
                    .where('date', '>=', start_date.isoformat())
                    .where('date', '<=', end_date.isoformat()))
            
            # Filtrar por tipos se especificado
            if log_types:
                query = query.where('log_type', 'in', log_types)
            
            # Ordenar por data e timestamp
            query = query.order_by('date').order_by('timestamp')
            
            # Executar query
            docs = query.stream()
            
            logs = []
            for doc in docs:
                log_data = doc.to_dict()
                log_data['log_id'] = doc.id
                logs.append(log_data)
            
            logger.info("Logs por período obtidos", 
                       user_id=user_id,
                       start_date=start_date.isoformat(),
                       end_date=end_date.isoformat(),
                       count=len(logs))
            
            return logs
            
        except Exception as e:
            logger.error("Erro ao obter logs por período", 
                        error=str(e),
                        user_id=user_id)
            raise
    
    # Métodos para agregações específicas
    
    async def get_weight_history(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Obtém histórico de peso do usuário
        
        Args:
            user_id: ID do usuário
            days: Número de dias para buscar
            
        Returns:
            List[Dict]: Histórico de peso
        """
        try:
            # Calcular data inicial
            end_date = date.today()
            start_date = date.fromordinal(end_date.toordinal() - days)
            
            # Buscar logs de peso
            query = (self.db.collection('daily_logs')
                    .where('user_id', '==', user_id)
                    .where('log_type', '==', 'body_weight')
                    .where('date', '>=', start_date.isoformat())
                    .where('date', '<=', end_date.isoformat())
                    .order_by('date'))
            
            docs = query.stream()
            
            weight_data = []
            for doc in docs:
                log_data = doc.to_dict()
                weight_entry = {
                    'date': log_data['date'],
                    'weight_kg': log_data['value'].get('weight_kg'),
                    'body_fat_percentage': log_data['value'].get('body_fat_percentage'),
                    'muscle_mass_kg': log_data['value'].get('muscle_mass_kg'),
                    'timestamp': log_data['timestamp']
                }
                weight_data.append(weight_entry)
            
            logger.info("Histórico de peso obtido", 
                       user_id=user_id,
                       count=len(weight_data))
            
            return weight_data
            
        except Exception as e:
            logger.error("Erro ao obter histórico de peso", 
                        error=str(e),
                        user_id=user_id)
            raise
    
    async def get_strength_progress(
        self,
        user_id: str,
        exercise_id: Optional[str] = None,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Obtém progresso de força do usuário
        
        Args:
            user_id: ID do usuário
            exercise_id: ID do exercício específico (opcional)
            days: Número de dias para buscar
            
        Returns:
            List[Dict]: Progresso de força
        """
        try:
            # Calcular data inicial
            end_date = date.today()
            start_date = date.fromordinal(end_date.toordinal() - days)
            
            # Buscar logs de séries
            query = (self.db.collection('daily_logs')
                    .where('user_id', '==', user_id)
                    .where('log_type', '==', 'set')
                    .where('date', '>=', start_date.isoformat())
                    .where('date', '<=', end_date.isoformat())
                    .order_by('date'))
            
            docs = query.stream()
            
            strength_data = []
            for doc in docs:
                log_data = doc.to_dict()
                set_data = log_data['value']
                
                # Filtrar por exercício se especificado
                if exercise_id and set_data.get('exercise_id') != exercise_id:
                    continue
                
                strength_entry = {
                    'date': log_data['date'],
                    'exercise_id': set_data.get('exercise_id'),
                    'exercise_name': set_data.get('exercise_name'),
                    'weight_kg': set_data.get('weight_kg'),
                    'reps_done': set_data.get('reps_done'),
                    'set_number': set_data.get('set_number'),
                    'timestamp': log_data['timestamp']
                }
                strength_data.append(strength_entry)
            
            logger.info("Progresso de força obtido", 
                       user_id=user_id,
                       exercise_id=exercise_id,
                       count=len(strength_data))
            
            return strength_data
            
        except Exception as e:
            logger.error("Erro ao obter progresso de força", 
                        error=str(e),
                        user_id=user_id)
            raise
    
    # Métodos auxiliares
    
    async def get_user_streak(self, user_id: str) -> int:
        """
        Calcula a sequência atual de dias seguindo o plano
        
        Args:
            user_id: ID do usuário
            
        Returns:
            int: Número de dias consecutivos
        """
        try:
            # Implementação simplificada - buscar logs dos últimos 30 dias
            end_date = date.today()
            start_date = date.fromordinal(end_date.toordinal() - 30)
            
            # Buscar logs de refeições (indicador de aderência)
            query = (self.db.collection('daily_logs')
                    .where('user_id', '==', user_id)
                    .where('log_type', '==', 'meal_checkin')
                    .where('date', '>=', start_date.isoformat())
                    .where('date', '<=', end_date.isoformat())
                    .order_by('date', direction=firestore.Query.DESCENDING))
            
            docs = query.stream()
            
            # Agrupar por data
            dates_with_logs = set()
            for doc in docs:
                log_data = doc.to_dict()
                dates_with_logs.add(log_data['date'])
            
            # Calcular sequência consecutiva a partir de hoje
            streak = 0
            current_date = end_date
            
            while current_date.isoformat() in dates_with_logs:
                streak += 1
                current_date = date.fromordinal(current_date.toordinal() - 1)
            
            logger.info("Streak calculado", user_id=user_id, streak=streak)
            return streak
            
        except Exception as e:
            logger.error("Erro ao calcular streak", error=str(e), user_id=user_id)
            return 0
    
    async def update_log(self, log_id: str, updates: Dict[str, Any]) -> bool:
        """
        Atualiza um log existente
        
        Args:
            log_id: ID do log
            updates: Dados para atualizar
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            # Adicionar timestamp de atualização
            updates['updated_at'] = datetime.utcnow()
            
            # Atualizar documento
            doc_ref = self.db.collection('daily_logs').document(log_id)
            doc_ref.update(updates)
            
            logger.info("Log atualizado", log_id=log_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar log", error=str(e), log_id=log_id)
            return False
    
    async def delete_log(self, log_id: str) -> bool:
        """
        Remove um log
        
        Args:
            log_id: ID do log
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            doc_ref = self.db.collection('daily_logs').document(log_id)
            doc_ref.delete()
            
            logger.info("Log removido", log_id=log_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao remover log", error=str(e), log_id=log_id)
            return False


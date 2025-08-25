"""
Serviço de conexão e operações com Firebase Firestore
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Union
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1 import AsyncClient
import structlog
from cachetools import TTLCache
import json

from ..config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

class FirebaseService:
    """Serviço para operações com Firebase Firestore"""
    
    def __init__(self):
        self.db: Optional[AsyncClient] = None
        self.app = None
        self._cache = TTLCache(maxsize=1000, ttl=settings.cache_ttl)
        
    async def initialize(self):
        """Inicializar conexão com Firebase"""
        try:
            # Verificar se já foi inicializado
            if not firebase_admin._apps:
                # Configurar credenciais
                if settings.firebase_credentials_path and os.path.exists(settings.firebase_credentials_path):
                    cred = credentials.Certificate(settings.firebase_credentials_path)
                    logger.info("Usando credenciais do arquivo", path=settings.firebase_credentials_path)
                else:
                    # Usar credenciais padrão do ambiente
                    cred = credentials.ApplicationDefault()
                    logger.info("Usando credenciais padrão do ambiente")
                
                # Inicializar app
                self.app = firebase_admin.initialize_app(cred, {
                    'projectId': settings.firebase_project_id
                })
                
                logger.info("Firebase inicializado", project_id=settings.firebase_project_id)
            else:
                self.app = firebase_admin.get_app()
                logger.info("Usando app Firebase existente")
            
            # Obter cliente Firestore
            self.db = firestore.AsyncClient()
            
            # Testar conexão
            await self._test_connection()
            
            logger.info("Conexão com Firestore estabelecida com sucesso")
            
        except Exception as e:
            logger.error("Erro ao inicializar Firebase", error=str(e))
            raise
    
    async def _test_connection(self):
        """Testar conexão com Firestore"""
        try:
            # Tentar acessar uma coleção
            collections = [col async for col in self.db.collections()]
            logger.info("Teste de conexão bem-sucedido", collections_count=len(collections))
        except Exception as e:
            logger.error("Falha no teste de conexão", error=str(e))
            raise
    
    def _get_cache_key(self, collection: str, doc_id: str = None, **kwargs) -> str:
        """Gerar chave de cache"""
        key_parts = [collection]
        if doc_id:
            key_parts.append(doc_id)
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Obter documento por ID"""
        cache_key = self._get_cache_key(collection, doc_id)
        
        # Verificar cache
        if cache_key in self._cache:
            logger.debug("Cache hit", collection=collection, doc_id=doc_id)
            return self._cache[cache_key]
        
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Armazenar no cache
                self._cache[cache_key] = data
                
                logger.debug("Documento obtido", collection=collection, doc_id=doc_id)
                return data
            else:
                logger.debug("Documento não encontrado", collection=collection, doc_id=doc_id)
                return None
                
        except Exception as e:
            logger.error("Erro ao obter documento", collection=collection, doc_id=doc_id, error=str(e))
            raise
    
    async def search_documents(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        search_term: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Buscar documentos com filtros e paginação
        
        Args:
            collection: Nome da coleção
            filters: Filtros a aplicar (campo: valor)
            search_term: Termo de busca
            search_fields: Campos para busca textual
            limit: Limite de resultados
            offset: Offset para paginação
            order_by: Campo para ordenação
            order_direction: Direção da ordenação (asc/desc)
        """
        try:
            query = self.db.collection(collection)
            
            # Aplicar filtros
            if filters:
                for field, value in filters.items():
                    if isinstance(value, dict):
                        # Filtros complexos (>=, <=, etc.)
                        for operator, filter_value in value.items():
                            query = query.where(filter=FieldFilter(field, operator, filter_value))
                    else:
                        # Filtro simples de igualdade
                        query = query.where(filter=FieldFilter(field, "==", value))
            
            # Busca textual (simulada com array-contains para tags)
            if search_term and search_fields:
                # Para busca textual real, seria necessário usar Algolia ou similar
                # Por enquanto, buscar em tags se disponível
                if "tags" in search_fields:
                    search_words = search_term.lower().split()
                    for word in search_words:
                        query = query.where(filter=FieldFilter("tags", "array_contains", word))
            
            # Ordenação
            if order_by:
                direction = firestore.Query.DESCENDING if order_direction == "desc" else firestore.Query.ASCENDING
                query = query.order_by(order_by, direction=direction)
            
            # Contar total (aproximado)
            total_query = query
            total_docs = [doc async for doc in total_query.stream()]
            total = len(total_docs)
            
            # Aplicar paginação
            if offset > 0:
                query = query.offset(offset)
            query = query.limit(limit)
            
            # Executar query
            docs = []
            async for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                docs.append(data)
            
            result = {
                "documents": docs,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(docs) < total
            }
            
            logger.debug(
                "Busca realizada",
                collection=collection,
                filters=filters,
                search_term=search_term,
                results_count=len(docs),
                total=total
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Erro na busca de documentos",
                collection=collection,
                filters=filters,
                error=str(e)
            )
            raise
    
    async def create_document(
        self,
        collection: str,
        data: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> str:
        """Criar novo documento"""
        try:
            # Adicionar timestamps
            from datetime import datetime
            now = datetime.utcnow()
            data['created_at'] = now
            data['updated_at'] = now
            
            if doc_id:
                doc_ref = self.db.collection(collection).document(doc_id)
                await doc_ref.set(data)
                created_id = doc_id
            else:
                doc_ref = self.db.collection(collection).document()
                await doc_ref.set(data)
                created_id = doc_ref.id
            
            # Invalidar cache relacionado
            self._invalidate_cache(collection)
            
            logger.info("Documento criado", collection=collection, doc_id=created_id)
            return created_id
            
        except Exception as e:
            logger.error("Erro ao criar documento", collection=collection, error=str(e))
            raise
    
    async def update_document(
        self,
        collection: str,
        doc_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Atualizar documento existente"""
        try:
            # Adicionar timestamp de atualização
            from datetime import datetime
            data['updated_at'] = datetime.utcnow()
            
            doc_ref = self.db.collection(collection).document(doc_id)
            await doc_ref.update(data)
            
            # Invalidar cache
            cache_key = self._get_cache_key(collection, doc_id)
            if cache_key in self._cache:
                del self._cache[cache_key]
            
            logger.info("Documento atualizado", collection=collection, doc_id=doc_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao atualizar documento", collection=collection, doc_id=doc_id, error=str(e))
            raise
    
    async def delete_document(self, collection: str, doc_id: str) -> bool:
        """Deletar documento"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            await doc_ref.delete()
            
            # Invalidar cache
            cache_key = self._get_cache_key(collection, doc_id)
            if cache_key in self._cache:
                del self._cache[cache_key]
            
            logger.info("Documento deletado", collection=collection, doc_id=doc_id)
            return True
            
        except Exception as e:
            logger.error("Erro ao deletar documento", collection=collection, doc_id=doc_id, error=str(e))
            raise
    
    async def batch_create_documents(
        self,
        collection: str,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """Criar múltiplos documentos em batch"""
        try:
            batch = self.db.batch()
            doc_ids = []
            
            from datetime import datetime
            now = datetime.utcnow()
            
            for data in documents:
                doc_ref = self.db.collection(collection).document()
                data['created_at'] = now
                data['updated_at'] = now
                batch.set(doc_ref, data)
                doc_ids.append(doc_ref.id)
            
            await batch.commit()
            
            # Invalidar cache relacionado
            self._invalidate_cache(collection)
            
            logger.info("Batch de documentos criado", collection=collection, count=len(doc_ids))
            return doc_ids
            
        except Exception as e:
            logger.error("Erro no batch create", collection=collection, error=str(e))
            raise
    
    async def get_distinct_values(self, collection: str, field: str) -> List[str]:
        """Obter valores únicos de um campo"""
        try:
            docs = []
            async for doc in self.db.collection(collection).stream():
                data = doc.to_dict()
                if field in data and data[field]:
                    docs.append(data[field])
            
            # Remover duplicatas e ordenar
            unique_values = sorted(list(set(docs)))
            
            logger.debug("Valores únicos obtidos", collection=collection, field=field, count=len(unique_values))
            return unique_values
            
        except Exception as e:
            logger.error("Erro ao obter valores únicos", collection=collection, field=field, error=str(e))
            raise
    
    def _invalidate_cache(self, collection: str):
        """Invalidar cache relacionado a uma coleção"""
        keys_to_remove = [key for key in self._cache.keys() if key.startswith(collection)]
        for key in keys_to_remove:
            del self._cache[key]
        
        logger.debug("Cache invalidado", collection=collection, keys_removed=len(keys_to_remove))
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar saúde da conexão"""
        try:
            # Tentar uma operação simples
            collections = [col async for col in self.db.collections()]
            
            return {
                "status": "healthy",
                "project_id": settings.firebase_project_id,
                "collections_count": len(collections),
                "cache_size": len(self._cache)
            }
            
        except Exception as e:
            logger.error("Health check falhou", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e)
            }


"""
Testes para o FirebaseService
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.firebase_service import FirebaseService
from config.settings import get_settings

class TestFirebaseService:
    """Testes para o FirebaseService"""
    
    @pytest.fixture
    def firebase_service(self):
        """Fixture para criar instância do FirebaseService"""
        return FirebaseService()
    
    @pytest.mark.asyncio
    async def test_initialization_success(self, firebase_service):
        """Testar inicialização bem-sucedida"""
        with patch('firebase_admin.initialize_app') as mock_init, \
             patch('firebase_admin._apps', []), \
             patch('firebase_admin.credentials.ApplicationDefault') as mock_cred, \
             patch('firestore.AsyncClient') as mock_client:
            
            mock_app = Mock()
            mock_init.return_value = mock_app
            mock_client_instance = AsyncMock()
            mock_client.return_value = mock_client_instance
            
            # Mock do teste de conexão
            mock_client_instance.collections.return_value.__aiter__ = AsyncMock(return_value=iter([]))
            
            await firebase_service.initialize()
            
            assert firebase_service.app == mock_app
            assert firebase_service.db == mock_client_instance
            mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_document_success(self, firebase_service):
        """Testar obtenção de documento com sucesso"""
        # Mock do cliente Firestore
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        # Mock do documento
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.id = "test_id"
        mock_doc.to_dict.return_value = {"name": "Test Food", "category": "test"}
        
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        result = await firebase_service.get_document("foods", "test_id")
        
        assert result is not None
        assert result["id"] == "test_id"
        assert result["name"] == "Test Food"
        mock_db.collection.assert_called_with("foods")
    
    @pytest.mark.asyncio
    async def test_get_document_not_found(self, firebase_service):
        """Testar documento não encontrado"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        result = await firebase_service.get_document("foods", "nonexistent")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_search_documents_with_filters(self, firebase_service):
        """Testar busca de documentos com filtros"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        # Mock da query
        mock_query = Mock()
        mock_db.collection.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Mock dos documentos
        mock_docs = [
            Mock(id="doc1", to_dict=lambda: {"name": "Food 1"}),
            Mock(id="doc2", to_dict=lambda: {"name": "Food 2"})
        ]
        
        # Mock do stream para contagem total
        mock_query.stream.return_value.__aiter__ = AsyncMock(return_value=iter(mock_docs))
        
        filters = {"category": "fruits"}
        result = await firebase_service.search_documents(
            collection="foods",
            filters=filters,
            limit=10,
            offset=0
        )
        
        assert "documents" in result
        assert "total" in result
        assert "has_more" in result
        assert len(result["documents"]) == 2
    
    @pytest.mark.asyncio
    async def test_create_document_success(self, firebase_service):
        """Testar criação de documento"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        mock_doc_ref = Mock()
        mock_doc_ref.id = "new_doc_id"
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        data = {"name": "New Food", "category": "test"}
        result = await firebase_service.create_document("foods", data)
        
        assert result == "new_doc_id"
        mock_doc_ref.set.assert_called_once()
        
        # Verificar se timestamps foram adicionados
        call_args = mock_doc_ref.set.call_args[0][0]
        assert "created_at" in call_args
        assert "updated_at" in call_args
    
    @pytest.mark.asyncio
    async def test_update_document_success(self, firebase_service):
        """Testar atualização de documento"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        mock_doc_ref = Mock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        data = {"name": "Updated Food"}
        result = await firebase_service.update_document("foods", "doc_id", data)
        
        assert result is True
        mock_doc_ref.update.assert_called_once()
        
        # Verificar se timestamp de atualização foi adicionado
        call_args = mock_doc_ref.update.call_args[0][0]
        assert "updated_at" in call_args
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, firebase_service):
        """Testar exclusão de documento"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        mock_doc_ref = Mock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        result = await firebase_service.delete_document("foods", "doc_id")
        
        assert result is True
        mock_doc_ref.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_batch_create_documents(self, firebase_service):
        """Testar criação em lote de documentos"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        mock_batch = Mock()
        mock_db.batch.return_value = mock_batch
        
        mock_doc_refs = [Mock(id=f"doc_{i}") for i in range(3)]
        mock_db.collection.return_value.document.side_effect = mock_doc_refs
        
        documents = [
            {"name": "Food 1"},
            {"name": "Food 2"},
            {"name": "Food 3"}
        ]
        
        result = await firebase_service.batch_create_documents("foods", documents)
        
        assert len(result) == 3
        assert result == ["doc_0", "doc_1", "doc_2"]
        mock_batch.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_distinct_values(self, firebase_service):
        """Testar obtenção de valores únicos"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        mock_docs = [
            Mock(to_dict=lambda: {"category": "fruits"}),
            Mock(to_dict=lambda: {"category": "vegetables"}),
            Mock(to_dict=lambda: {"category": "fruits"}),  # Duplicata
        ]
        
        mock_db.collection.return_value.stream.return_value.__aiter__ = AsyncMock(return_value=iter(mock_docs))
        
        result = await firebase_service.get_distinct_values("foods", "category")
        
        assert len(result) == 2
        assert "fruits" in result
        assert "vegetables" in result
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, firebase_service):
        """Testar health check bem-sucedido"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        mock_collections = [Mock(), Mock()]
        mock_db.collections.return_value.__aiter__ = AsyncMock(return_value=iter(mock_collections))
        
        result = await firebase_service.health_check()
        
        assert result["status"] == "healthy"
        assert result["collections_count"] == 2
        assert "cache_size" in result
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, firebase_service):
        """Testar health check com falha"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        mock_db.collections.side_effect = Exception("Connection failed")
        
        result = await firebase_service.health_check()
        
        assert result["status"] == "unhealthy"
        assert "error" in result
    
    def test_cache_functionality(self, firebase_service):
        """Testar funcionalidade de cache"""
        # Testar geração de chave de cache
        key1 = firebase_service._get_cache_key("foods", "doc1")
        key2 = firebase_service._get_cache_key("foods", "doc1", filter="test")
        
        assert key1 == "foods:doc1"
        assert key2 == "foods:doc1:filter:test"
        
        # Testar invalidação de cache
        firebase_service._cache["foods:doc1"] = {"test": "data"}
        firebase_service._cache["exercises:doc1"] = {"test": "data"}
        
        firebase_service._invalidate_cache("foods")
        
        assert "foods:doc1" not in firebase_service._cache
        assert "exercises:doc1" in firebase_service._cache

class TestFirebaseServiceErrors:
    """Testes de tratamento de erros do FirebaseService"""
    
    @pytest.fixture
    def firebase_service(self):
        return FirebaseService()
    
    @pytest.mark.asyncio
    async def test_initialization_failure(self, firebase_service):
        """Testar falha na inicialização"""
        with patch('firebase_admin.initialize_app') as mock_init:
            mock_init.side_effect = Exception("Firebase initialization failed")
            
            with pytest.raises(Exception):
                await firebase_service.initialize()
    
    @pytest.mark.asyncio
    async def test_get_document_error(self, firebase_service):
        """Testar erro na obtenção de documento"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        mock_db.collection.return_value.document.return_value.get.side_effect = Exception("Firestore error")
        
        with pytest.raises(Exception):
            await firebase_service.get_document("foods", "test_id")
    
    @pytest.mark.asyncio
    async def test_search_documents_error(self, firebase_service):
        """Testar erro na busca de documentos"""
        mock_db = AsyncMock()
        firebase_service.db = mock_db
        
        mock_db.collection.side_effect = Exception("Query error")
        
        with pytest.raises(Exception):
            await firebase_service.search_documents("foods")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


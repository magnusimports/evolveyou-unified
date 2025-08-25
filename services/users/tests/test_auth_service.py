"""
Testes para o serviço de autenticação
"""

import pytest
from datetime import datetime, date
from unittest.mock import Mock, AsyncMock, patch
import jwt

from src.services.auth_service import AuthService
from src.services.firebase_service import FirebaseService
from src.models.user import UserRegistration, SocialLogin, UserProfile, Gender
from src.config.settings import get_settings

settings = get_settings()

@pytest.fixture
def mock_firebase_service():
    """Mock do serviço Firebase"""
    mock = Mock(spec=FirebaseService)
    mock.create_user = AsyncMock()
    mock.get_user_by_email = AsyncMock()
    mock.create_firebase_user = AsyncMock()
    mock.update_user = AsyncMock()
    mock.log_auth_event = AsyncMock()
    mock.save_refresh_token = AsyncMock()
    mock.get_refresh_token = AsyncMock()
    mock.revoke_refresh_token = AsyncMock()
    return mock

@pytest.fixture
def auth_service(mock_firebase_service):
    """Instância do serviço de autenticação"""
    return AuthService(mock_firebase_service)

@pytest.fixture
def sample_user_registration():
    """Dados de exemplo para registro"""
    return UserRegistration(
        email="test@evolveyou.com.br",
        password="MinhaSenh@123",
        name="João Silva",
        date_of_birth=date(1990, 5, 15),
        gender=Gender.MALE,
        terms_accepted=True,
        privacy_accepted=True,
        marketing_consent=False
    )

@pytest.fixture
def sample_user_profile():
    """Perfil de usuário de exemplo"""
    return UserProfile(
        id="user123",
        email="test@evolveyou.com.br",
        name="João Silva",
        date_of_birth=date(1990, 5, 15),
        gender=Gender.MALE,
        is_active=True,
        is_verified=False,
        is_premium=False,
        onboarding_completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        terms_accepted=True,
        privacy_accepted=True,
        marketing_consent=False
    )

class TestAuthService:
    """Testes para AuthService"""
    
    def test_hash_password(self, auth_service):
        """Testar criptografia de senha"""
        password = "MinhaSenh@123"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50  # Hash bcrypt é longo
        assert hashed.startswith("$2b$")  # Prefixo bcrypt
    
    def test_verify_password(self, auth_service):
        """Testar verificação de senha"""
        password = "MinhaSenh@123"
        hashed = auth_service.hash_password(password)
        
        # Senha correta
        assert auth_service.verify_password(password, hashed) is True
        
        # Senha incorreta
        assert auth_service.verify_password("SenhaErrada", hashed) is False
    
    def test_generate_jwt_token(self, auth_service):
        """Testar geração de token JWT"""
        user_id = "user123"
        
        # Token de acesso
        access_token = auth_service.generate_jwt_token(user_id, "access")
        payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert payload["iss"] == "evolveyou-users-service"
        
        # Token de refresh
        refresh_token = auth_service.generate_jwt_token(user_id, "refresh")
        payload = jwt.decode(refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
    
    def test_verify_jwt_token(self, auth_service):
        """Testar verificação de token JWT"""
        user_id = "user123"
        token = auth_service.generate_jwt_token(user_id, "access")
        
        # Token válido
        payload = auth_service.verify_jwt_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        
        # Token inválido
        with pytest.raises(ValueError, match="Token inválido"):
            auth_service.verify_jwt_token("token_invalido")
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, mock_firebase_service, sample_user_registration):
        """Testar registro de usuário com sucesso"""
        # Configurar mocks
        mock_firebase_service.create_user.return_value = "user123"
        mock_firebase_service.create_firebase_user.return_value = "firebase_uid123"
        
        # Executar registro
        user = await auth_service.register_user(sample_user_registration)
        
        # Verificar resultado
        assert isinstance(user, UserProfile)
        assert user.email == sample_user_registration.email
        assert user.name == sample_user_registration.name
        assert user.is_active is True
        assert user.is_verified is False
        
        # Verificar chamadas
        mock_firebase_service.create_user.assert_called_once()
        mock_firebase_service.create_firebase_user.assert_called_once()
        mock_firebase_service.update_user.assert_called_once()
        mock_firebase_service.log_auth_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_firebase_service, sample_user_profile):
        """Testar autenticação com sucesso"""
        # Preparar dados do usuário com senha hasheada
        password = "MinhaSenh@123"
        hashed_password = auth_service.hash_password(password)
        
        user_data = sample_user_profile.dict()
        user_data["password_hash"] = hashed_password
        user_data["date_of_birth"] = user_data["date_of_birth"].isoformat()
        
        # Configurar mock
        mock_firebase_service.get_user_by_email.return_value = user_data
        
        # Executar autenticação
        user = await auth_service.authenticate_user(sample_user_profile.email, password)
        
        # Verificar resultado
        assert isinstance(user, UserProfile)
        assert user.email == sample_user_profile.email
        assert user.id == sample_user_profile.id
        
        # Verificar chamadas
        mock_firebase_service.get_user_by_email.assert_called_once_with(sample_user_profile.email)
        mock_firebase_service.log_auth_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, auth_service, mock_firebase_service, sample_user_profile):
        """Testar autenticação com senha inválida"""
        # Preparar dados com senha diferente
        correct_password = "MinhaSenh@123"
        wrong_password = "SenhaErrada"
        hashed_password = auth_service.hash_password(correct_password)
        
        user_data = sample_user_profile.dict()
        user_data["password_hash"] = hashed_password
        user_data["date_of_birth"] = user_data["date_of_birth"].isoformat()
        
        # Configurar mock
        mock_firebase_service.get_user_by_email.return_value = user_data
        
        # Executar autenticação
        user = await auth_service.authenticate_user(sample_user_profile.email, wrong_password)
        
        # Verificar que retorna None
        assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service, mock_firebase_service):
        """Testar autenticação com usuário não encontrado"""
        # Configurar mock para retornar None
        mock_firebase_service.get_user_by_email.return_value = None
        
        # Executar autenticação
        user = await auth_service.authenticate_user("naoexiste@test.com", "senha")
        
        # Verificar que retorna None
        assert user is None
    
    @pytest.mark.asyncio
    async def test_generate_tokens(self, auth_service, mock_firebase_service):
        """Testar geração de tokens"""
        user_id = "user123"
        
        # Executar geração
        tokens = await auth_service.generate_tokens(user_id)
        
        # Verificar tokens
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.expires_in == settings.jwt_access_token_expire_minutes * 60
        
        # Verificar que refresh token foi salvo
        mock_firebase_service.save_refresh_token.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_refresh_tokens_success(self, auth_service, mock_firebase_service):
        """Testar renovação de tokens com sucesso"""
        user_id = "user123"
        old_refresh_token = auth_service.generate_jwt_token(user_id, "refresh")
        
        # Configurar mocks
        mock_firebase_service.get_refresh_token.return_value = {
            "user_id": user_id,
            "token": old_refresh_token,
            "is_active": True
        }
        
        # Executar renovação
        new_tokens = await auth_service.refresh_tokens(old_refresh_token)
        
        # Verificar resultado
        assert new_tokens.access_token is not None
        assert new_tokens.refresh_token is not None
        assert new_tokens.refresh_token != old_refresh_token
        
        # Verificar chamadas
        mock_firebase_service.get_refresh_token.assert_called_once_with(old_refresh_token)
        mock_firebase_service.revoke_refresh_token.assert_called_once_with(old_refresh_token)
        mock_firebase_service.save_refresh_token.assert_called()
    
    @pytest.mark.asyncio
    async def test_refresh_tokens_invalid(self, auth_service, mock_firebase_service):
        """Testar renovação com token inválido"""
        # Configurar mock para retornar None
        mock_firebase_service.get_refresh_token.return_value = None
        
        # Executar e verificar exceção
        with pytest.raises(ValueError, match="Refresh token inválido"):
            await auth_service.refresh_tokens("token_invalido")
    
    @pytest.mark.asyncio
    async def test_verify_google_token(self, auth_service):
        """Testar verificação de token Google"""
        with patch('httpx.AsyncClient') as mock_client:
            # Configurar mock da resposta
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user_id": "google123",
                "email": "test@gmail.com",
                "name": "João Silva",
                "verified_email": True
            }
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Executar verificação
            result = await auth_service._verify_google_token("google_token")
            
            # Verificar resultado
            assert result["provider"] == "google"
            assert result["email"] == "test@gmail.com"
            assert result["name"] == "João Silva"
            assert result["verified_email"] is True
    
    @pytest.mark.asyncio
    async def test_get_or_create_social_user_existing(self, auth_service, mock_firebase_service, sample_user_profile):
        """Testar login social com usuário existente"""
        user_info = {
            "provider": "google",
            "provider_id": "google123",
            "email": sample_user_profile.email,
            "name": sample_user_profile.name,
            "verified_email": True
        }
        
        # Configurar mock para usuário existente
        user_data = sample_user_profile.dict()
        user_data["date_of_birth"] = user_data["date_of_birth"].isoformat()
        mock_firebase_service.get_user_by_email.return_value = user_data
        
        # Executar
        user = await auth_service.get_or_create_social_user(user_info)
        
        # Verificar resultado
        assert isinstance(user, UserProfile)
        assert user.email == sample_user_profile.email
        
        # Verificar que atualizou dados sociais
        mock_firebase_service.update_user.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_or_create_social_user_new(self, auth_service, mock_firebase_service):
        """Testar login social com usuário novo"""
        user_info = {
            "provider": "google",
            "provider_id": "google123",
            "email": "novo@gmail.com",
            "name": "Usuário Novo",
            "verified_email": True
        }
        
        # Configurar mocks
        mock_firebase_service.get_user_by_email.return_value = None  # Usuário não existe
        mock_firebase_service.create_user.return_value = "new_user_id"
        
        # Executar
        user = await auth_service.get_or_create_social_user(user_info)
        
        # Verificar resultado
        assert isinstance(user, UserProfile)
        assert user.email == "novo@gmail.com"
        assert user.name == "Usuário Novo"
        assert user.is_verified is True  # Email verificado pelo Google
        
        # Verificar chamadas
        mock_firebase_service.create_user.assert_called_once()
        mock_firebase_service.log_auth_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_last_login(self, auth_service, mock_firebase_service):
        """Testar atualização do último login"""
        user_id = "user123"
        
        # Executar
        result = await auth_service.update_last_login(user_id)
        
        # Verificar resultado
        assert result is True
        
        # Verificar chamada
        mock_firebase_service.update_user.assert_called_once()
        call_args = mock_firebase_service.update_user.call_args
        assert call_args[0][0] == user_id
        assert "last_login" in call_args[0][1]
        assert "updated_at" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_service, mock_firebase_service, sample_user_profile):
        """Testar alteração de senha com sucesso"""
        old_password = "SenhaAntiga123"
        new_password = "SenhaNova456"
        
        # Preparar dados do usuário
        user_data = sample_user_profile.dict()
        user_data["password_hash"] = auth_service.hash_password(old_password)
        
        # Configurar mock
        mock_firebase_service.get_user_by_id.return_value = user_data
        
        # Executar
        result = await auth_service.change_password(sample_user_profile.id, old_password, new_password)
        
        # Verificar resultado
        assert result is True
        
        # Verificar chamadas
        mock_firebase_service.get_user_by_id.assert_called_once_with(sample_user_profile.id)
        mock_firebase_service.update_user.assert_called_once()
        mock_firebase_service.log_auth_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, auth_service, mock_firebase_service, sample_user_profile):
        """Testar alteração de senha com senha atual incorreta"""
        old_password = "SenhaAntiga123"
        wrong_old_password = "SenhaErrada"
        new_password = "SenhaNova456"
        
        # Preparar dados do usuário
        user_data = sample_user_profile.dict()
        user_data["password_hash"] = auth_service.hash_password(old_password)
        
        # Configurar mock
        mock_firebase_service.get_user_by_id.return_value = user_data
        
        # Executar e verificar exceção
        with pytest.raises(ValueError, match="Senha atual incorreta"):
            await auth_service.change_password(sample_user_profile.id, wrong_old_password, new_password)


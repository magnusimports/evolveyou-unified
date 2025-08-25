"""
EvolveYou Users Service
Microserviço responsável por gerenciar usuários, autenticação e onboarding
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import uvicorn
from typing import Dict, Any
import structlog

from config.settings import get_settings
from services.firebase_service import FirebaseService
from services.auth_service import AuthService
from services.user_service import UserService
from services.calorie_service import CalorieService
from services.communication_service import CommunicationService
from models.user import (
    UserRegistration, SocialLogin, OnboardingData, 
    AuthResponse, UserResponse, AuthTokens
)
from middleware.auth import verify_token, get_current_user
from middleware.logging import setup_logging
from middleware.rate_limit import rate_limit

# Configurar logging estruturado
setup_logging()
logger = structlog.get_logger()

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    logger.info("Iniciando Users Service", version=settings.version)
    
    # Inicializar serviços
    firebase_service = FirebaseService()
    await firebase_service.initialize()
    
    # Armazenar serviços no estado da aplicação
    app.state.firebase_service = firebase_service
    app.state.auth_service = AuthService(firebase_service)
    app.state.user_service = UserService(firebase_service)
    app.state.calorie_service = CalorieService()
    app.state.communication_service = CommunicationService()
    
    logger.info("Users Service iniciado com sucesso")
    
    yield
    
    logger.info("Finalizando Users Service")

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    description="Microserviço para gestão de usuários, autenticação e onboarding da plataforma EvolveYou",
    version=settings.version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

# Dependency para obter serviços
def get_auth_service() -> AuthService:
    return app.state.auth_service

def get_user_service() -> UserService:
    return app.state.user_service

def get_calorie_service() -> CalorieService:
    return app.state.calorie_service

def get_communication_service() -> CommunicationService:
    return app.state.communication_service

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde"""
    try:
        # Verificar conexão com Firebase
        firebase_status = "healthy"
        try:
            app.state.firebase_service.db.collection("health_check").limit(1).get()
        except Exception as e:
            firebase_status = "unhealthy"
            logger.error("Firebase health check failed", error=str(e))
        
        return {
            "status": "healthy" if firebase_status == "healthy" else "degraded",
            "timestamp": "2025-08-09T17:30:00Z",
            "version": settings.version,
            "services": {
                "firebase": firebase_status,
                "auth": "healthy",
                "users": "healthy",
                "calories": "healthy"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-08-09T17:30:00Z"
            }
        )

# Endpoints de Autenticação
@app.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@rate_limit(requests=5, window=300)  # 5 registros por 5 minutos
async def register_user(
    user_data: UserRegistration,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
):
    """Registrar novo usuário"""
    try:
        logger.info("Iniciando registro de usuário", email=user_data.email)
        
        # Verificar se email já existe
        if await user_service.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado"
            )
        
        # Criar usuário
        user = await auth_service.register_user(user_data)
        
        # Gerar tokens
        tokens = await auth_service.generate_tokens(user.id)
        
        logger.info("Usuário registrado com sucesso", user_id=user.id)
        
        return AuthResponse(
            user=UserResponse(**user.dict()),
            tokens=tokens,
            message="Usuário criado com sucesso"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro no registro", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@app.post("/auth/login", response_model=AuthResponse)
@rate_limit(requests=10, window=300)  # 10 tentativas por 5 minutos
async def login_user(
    email: str,
    password: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Fazer login com email e senha"""
    try:
        logger.info("Tentativa de login", email=email)
        
        # Autenticar usuário
        user = await auth_service.authenticate_user(email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )
        
        # Gerar tokens
        tokens = await auth_service.generate_tokens(user.id)
        
        # Atualizar último login
        await auth_service.update_last_login(user.id)
        
        logger.info("Login realizado com sucesso", user_id=user.id)
        
        return AuthResponse(
            user=UserResponse(**user.dict()),
            tokens=tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro no login", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@app.post("/auth/social-login", response_model=AuthResponse)
@rate_limit(requests=10, window=300)
async def social_login(
    social_data: SocialLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login com provedores sociais (Google, Apple, Facebook)"""
    try:
        logger.info("Login social", provider=social_data.provider)
        
        # Verificar token do provedor
        user_info = await auth_service.verify_social_token(social_data)
        
        # Buscar ou criar usuário
        user = await auth_service.get_or_create_social_user(user_info)
        
        # Gerar tokens
        tokens = await auth_service.generate_tokens(user.id)
        
        # Atualizar último login
        await auth_service.update_last_login(user.id)
        
        logger.info("Login social realizado", user_id=user.id, provider=social_data.provider)
        
        return AuthResponse(
            user=UserResponse(**user.dict()),
            tokens=tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro no login social", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@app.post("/auth/refresh", response_model=AuthTokens)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Renovar token de acesso"""
    try:
        tokens = await auth_service.refresh_tokens(refresh_token)
        return tokens
    except Exception as e:
        logger.error("Erro ao renovar token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de renovação inválido"
        )

# Endpoints de Usuário
@app.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """Obter perfil do usuário atual"""
    return UserResponse(**current_user)

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Obter perfil de usuário por ID"""
    try:
        # Verificar se é o próprio usuário ou admin
        if current_user["id"] != user_id and not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return UserResponse(**user.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar usuário", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# Endpoint de Onboarding
@app.post("/onboarding/submit", response_model=Dict[str, Any])
@rate_limit(requests=3, window=300)  # 3 tentativas por 5 minutos
async def submit_onboarding(
    onboarding_data: OnboardingData,
    user_service: UserService = Depends(get_user_service),
    calorie_service: CalorieService = Depends(get_calorie_service),
    communication_service: CommunicationService = Depends(get_communication_service),
    current_user: dict = Depends(get_current_user)
):
    """Submeter dados completos do onboarding"""
    try:
        user_id = current_user["id"]
        logger.info("Iniciando onboarding", user_id=user_id)
        
        # Validar dados do onboarding
        await user_service.validate_onboarding_data(onboarding_data)
        
        # Calcular metas calóricas
        calorie_calculation = await calorie_service.calculate_calories(
            onboarding_data.health_assessment,
            onboarding_data.lifestyle_assessment,
            onboarding_data.fitness_goals,
            current_user["gender"],
            current_user["date_of_birth"]
        )
        
        # Salvar dados no perfil do usuário
        await user_service.complete_onboarding(
            user_id, 
            onboarding_data, 
            calorie_calculation
        )
        
        # Disparar evento para geração de planos
        await communication_service.notify_onboarding_completed(
            user_id, 
            onboarding_data.fitness_goals,
            calorie_calculation
        )
        
        logger.info("Onboarding concluído", user_id=user_id)
        
        return {
            "message": "Onboarding concluído com sucesso",
            "calorie_calculation": calorie_calculation.dict(),
            "next_steps": [
                "Aguarde a geração dos seus planos personalizados",
                "Explore o conteúdo disponível na plataforma",
                "Configure suas preferências de notificação"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro no onboarding", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@app.get("/onboarding/status")
async def get_onboarding_status(
    current_user: dict = Depends(get_current_user)
):
    """Verificar status do onboarding"""
    return {
        "completed": current_user.get("onboarding_completed", False),
        "steps_completed": current_user.get("onboarding_steps_completed", []),
        "next_step": current_user.get("next_onboarding_step", "personal_info")
    }

# Endpoints de Cálculo Calórico
@app.post("/calories/recalculate")
async def recalculate_calories(
    user_service: UserService = Depends(get_user_service),
    calorie_service: CalorieService = Depends(get_calorie_service),
    current_user: dict = Depends(get_current_user)
):
    """Recalcular metas calóricas"""
    try:
        user_id = current_user["id"]
        
        # Buscar dados do usuário
        user = await user_service.get_user_by_id(user_id)
        
        if not user.onboarding_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Onboarding não concluído"
            )
        
        # Recalcular calorias
        calorie_calculation = await calorie_service.calculate_calories(
            user.onboarding_data.health_assessment,
            user.onboarding_data.lifestyle_assessment,
            user.onboarding_data.fitness_goals,
            user.gender,
            user.date_of_birth
        )
        
        # Atualizar no perfil
        await user_service.update_calorie_calculation(user_id, calorie_calculation)
        
        return {
            "message": "Calorias recalculadas com sucesso",
            "calorie_calculation": calorie_calculation.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao recalcular calorias", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


"""
EvolveYou Plans Service - Fábrica de Planos Personalizados
"""

import logging
import structlog
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configurações e dependências
from config.settings import get_settings
from services.firebase_service import FirebaseService
from services.plan_service import PlanService
from middleware.logging import setup_logging, LoggingMiddleware
from middleware.auth import AuthMiddleware
from middleware.rate_limit import RateLimitMiddleware

# Modelos
from models.plan import (
    DietPlanResponse, WorkoutPlanResponse, 
    PresentationResponse, WeeklyScheduleResponse,
    ErrorResponse
)

# Configurar logging estruturado
setup_logging()
logger = structlog.get_logger(__name__)

# Instâncias globais de serviços
firebase_service = FirebaseService()
plan_service = PlanService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    settings = get_settings()
    
    # Startup
    logger.info("Iniciando Plans Service", version=settings.version)
    
    try:
        # Inicializar Firebase
        await firebase_service.initialize()
        logger.info("Firebase inicializado com sucesso")
        
        # Inicializar Plan Service
        await plan_service.initialize(firebase_service)
        logger.info("Plan Service inicializado com sucesso")
        
        # Verificar conectividade com outros serviços
        await plan_service.health_check_services()
        logger.info("Health check de serviços externos concluído")
        
    except Exception as e:
        logger.error("Erro ao inicializar serviços", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Finalizando Plans Service")
    await firebase_service.close()
    await plan_service.close()

# Criar aplicação FastAPI
def create_app() -> FastAPI:
    """Criar e configurar aplicação FastAPI"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Microserviço responsável pela geração de planos personalizados de dieta e treino",
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
    
    # Adicionar middlewares customizados
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)
    
    return app

app = create_app()

# Dependências

async def get_plan_service() -> PlanService:
    """Dependência para obter instância do PlanService"""
    return plan_service

async def get_current_user(request: Request) -> dict:
    """Dependência para obter usuário atual do token JWT"""
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="Token de autenticação inválido")
    return user

# Handlers de erro

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para exceções HTTP"""
    logger.warning(
        "HTTP Exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            details={"status_code": exc.status_code}
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(
        "Erro interno do servidor",
        error=str(exc),
        path=request.url.path,
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Erro interno do servidor",
            details={"type": type(exc).__name__}
        ).dict()
    )

# Rotas de sistema

@app.get("/health")
async def health_check():
    """Health check do serviço"""
    try:
        # Verificar Firebase
        firebase_status = await firebase_service.health_check()
        
        # Verificar serviços externos
        services_status = await plan_service.health_check_services()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": get_settings().version,
            "services": {
                "firebase": firebase_status,
                "external_services": services_status
            }
        }
    except Exception as e:
        logger.error("Health check falhou", error=str(e))
        raise HTTPException(status_code=503, detail="Serviço indisponível")

@app.get("/metrics")
async def get_metrics():
    """Métricas do serviço"""
    try:
        metrics = await plan_service.get_metrics()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
    except Exception as e:
        logger.error("Erro ao obter métricas", error=str(e))
        raise HTTPException(status_code=500, detail="Erro ao obter métricas")

# Rotas principais da API

@app.get("/plan/diet", response_model=DietPlanResponse)
async def get_diet_plan(
    date: str = None,
    user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Retorna o plano de dieta personalizado para o usuário
    
    - **date**: Data do plano (formato YYYY-MM-DD). Se não informado, usa data atual
    """
    try:
        logger.info("Gerando plano de dieta", user_id=user["user_id"], date=date)
        
        diet_plan = await service.generate_diet_plan(
            user_id=user["user_id"],
            target_date=date
        )
        
        logger.info("Plano de dieta gerado com sucesso", user_id=user["user_id"])
        
        return DietPlanResponse(
            data=diet_plan,
            message="Plano de dieta gerado com sucesso"
        )
        
    except Exception as e:
        logger.error("Erro ao gerar plano de dieta", user_id=user["user_id"], error=str(e))
        raise HTTPException(status_code=500, detail="Erro ao gerar plano de dieta")

@app.get("/plan/workout", response_model=WorkoutPlanResponse)
async def get_workout_plan(
    date: str = None,
    user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Retorna o plano de treino personalizado para o usuário
    
    - **date**: Data do plano (formato YYYY-MM-DD). Se não informado, usa data atual
    """
    try:
        logger.info("Gerando plano de treino", user_id=user["user_id"], date=date)
        
        workout_plan = await service.generate_workout_plan(
            user_id=user["user_id"],
            target_date=date
        )
        
        logger.info("Plano de treino gerado com sucesso", user_id=user["user_id"])
        
        return WorkoutPlanResponse(
            data=workout_plan,
            message="Plano de treino gerado com sucesso"
        )
        
    except Exception as e:
        logger.error("Erro ao gerar plano de treino", user_id=user["user_id"], error=str(e))
        raise HTTPException(status_code=500, detail="Erro ao gerar plano de treino")

@app.get("/plan/presentation", response_model=PresentationResponse)
async def get_plan_presentation(
    date: str = None,
    user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Retorna a apresentação personalizada do plano do usuário
    
    - **date**: Data do plano (formato YYYY-MM-DD). Se não informado, usa data atual
    """
    try:
        logger.info("Gerando apresentação do plano", user_id=user["user_id"], date=date)
        
        presentation = await service.generate_plan_presentation(
            user_id=user["user_id"],
            target_date=date
        )
        
        logger.info("Apresentação do plano gerada com sucesso", user_id=user["user_id"])
        
        return PresentationResponse(
            data=presentation,
            message="Apresentação do plano gerada com sucesso"
        )
        
    except Exception as e:
        logger.error("Erro ao gerar apresentação do plano", user_id=user["user_id"], error=str(e))
        raise HTTPException(status_code=500, detail="Erro ao gerar apresentação do plano")

@app.get("/plan/weekly-schedule", response_model=WeeklyScheduleResponse)
async def get_weekly_schedule(
    week_start: str = None,
    user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Retorna o cronograma semanal completo do usuário
    
    - **week_start**: Data de início da semana (formato YYYY-MM-DD). Se não informado, usa semana atual
    """
    try:
        logger.info("Gerando cronograma semanal", user_id=user["user_id"], week_start=week_start)
        
        weekly_schedule = await service.generate_weekly_schedule(
            user_id=user["user_id"],
            week_start_date=week_start
        )
        
        logger.info("Cronograma semanal gerado com sucesso", user_id=user["user_id"])
        
        return WeeklyScheduleResponse(
            data=weekly_schedule,
            message="Cronograma semanal gerado com sucesso"
        )
        
    except Exception as e:
        logger.error("Erro ao gerar cronograma semanal", user_id=user["user_id"], error=str(e))
        raise HTTPException(status_code=500, detail="Erro ao gerar cronograma semanal")

# Rotas administrativas (opcional)

@app.post("/admin/regenerate-plans")
async def regenerate_user_plans(
    user_id: str,
    force: bool = False,
    user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Regenera todos os planos de um usuário (apenas para administradores)
    """
    # Verificar se usuário é admin (implementar lógica de autorização)
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        logger.info("Regenerando planos do usuário", target_user_id=user_id, admin_user=user["user_id"])
        
        result = await service.regenerate_user_plans(user_id, force=force)
        
        logger.info("Planos regenerados com sucesso", target_user_id=user_id)
        
        return {
            "success": True,
            "message": "Planos regenerados com sucesso",
            "details": result
        }
        
    except Exception as e:
        logger.error("Erro ao regenerar planos", target_user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Erro ao regenerar planos")

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


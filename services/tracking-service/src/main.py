"""
Aplicação principal do Tracking Service
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

import structlog
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from config.settings import get_settings
from models.tracking import ErrorResponse, ServiceHealthCheck
from services.firebase_service import FirebaseService
from services.cache_service import CacheService
from middleware.logging import setup_logging, LoggingMiddleware
from middleware.auth import AuthMiddleware
from middleware.rate_limit import RateLimitMiddleware
from routes import logging_routes, dashboard_routes, progress_routes

# Configurar logging estruturado
setup_logging()
logger = structlog.get_logger(__name__)

# Variáveis globais para serviços
firebase_service: FirebaseService = None
cache_service: CacheService = None
app_start_time: datetime = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    global firebase_service, cache_service, app_start_time
    
    settings = get_settings()
    app_start_time = datetime.utcnow()
    
    logger.info("Iniciando Tracking Service", version=settings.app_version)
    
    try:
        # Inicializar Firebase
        firebase_service = FirebaseService()
        await firebase_service.initialize()
        logger.info("Firebase inicializado com sucesso")
        
        # Inicializar Cache
        cache_service = CacheService()
        await cache_service.initialize()
        logger.info("Cache inicializado com sucesso")
        
        # Adicionar serviços ao estado da aplicação
        app.state.firebase = firebase_service
        app.state.cache = cache_service
        
        logger.info("Tracking Service iniciado com sucesso")
        
        yield
        
    except Exception as e:
        logger.error("Erro ao inicializar serviços", error=str(e))
        raise
    finally:
        # Cleanup
        logger.info("Finalizando Tracking Service")
        
        if cache_service:
            await cache_service.close()
        
        if firebase_service:
            await firebase_service.close()


# Criar aplicação FastAPI
def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Microserviço de tracking e monitoramento da EvolveYou",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Em produção, especificar domínios
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Adicionar middlewares customizados
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitMiddleware)
    
    # Registrar rotas
    app.include_router(logging_routes.router, prefix="/log", tags=["Logging"])
    app.include_router(dashboard_routes.router, prefix="/dashboard", tags=["Dashboard"])
    app.include_router(progress_routes.router, prefix="/progress", tags=["Progress"])
    
    # Handlers de erro
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handler para exceções HTTP"""
        logger.warning("HTTP Exception", 
                      status_code=exc.status_code, 
                      detail=exc.detail,
                      path=request.url.path)
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error_code=f"HTTP_{exc.status_code}",
                message=exc.detail,
                details={"path": str(request.url.path)}
            ).dict()
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handler para erros de validação"""
        logger.warning("Validation Error", 
                      errors=exc.errors(),
                      path=request.url.path)
        
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error_code="VALIDATION_ERROR",
                message="Dados de entrada inválidos",
                details={"errors": exc.errors()}
            ).dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handler para exceções gerais"""
        logger.error("Unhandled Exception", 
                    error=str(exc),
                    path=request.url.path,
                    exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error_code="INTERNAL_ERROR",
                message="Erro interno do servidor",
                details={"path": str(request.url.path)} if settings.debug else None
            ).dict()
        )
    
    return app


# Criar instância da aplicação
app = create_app()


@app.get("/", response_model=Dict[str, Any])
async def root():
    """Endpoint raiz com informações básicas"""
    settings = get_settings()
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", response_model=ServiceHealthCheck)
async def health_check():
    """Endpoint de health check"""
    global app_start_time
    settings = get_settings()
    
    # Calcular uptime
    uptime = (datetime.utcnow() - app_start_time).total_seconds() if app_start_time else 0
    
    # Verificar dependências
    dependencies = {}
    
    try:
        # Verificar Firebase
        if hasattr(app.state, 'firebase') and app.state.firebase:
            await app.state.firebase.health_check()
            dependencies["firebase"] = "healthy"
        else:
            dependencies["firebase"] = "unhealthy"
    except Exception:
        dependencies["firebase"] = "unhealthy"
    
    try:
        # Verificar Cache
        if hasattr(app.state, 'cache') and app.state.cache:
            await app.state.cache.health_check()
            dependencies["cache"] = "healthy"
        else:
            dependencies["cache"] = "unhealthy"
    except Exception:
        dependencies["cache"] = "unhealthy"
    
    # Determinar status geral
    all_healthy = all(status == "healthy" for status in dependencies.values())
    overall_status = "healthy" if all_healthy else "unhealthy"
    
    return ServiceHealthCheck(
        service_name=settings.app_name,
        status=overall_status,
        version=settings.app_version,
        uptime_seconds=uptime,
        dependencies=dependencies
    )


@app.get("/metrics")
async def metrics():
    """Endpoint de métricas para monitoramento"""
    # Implementar métricas customizadas se necessário
    return {
        "requests_total": "TODO",
        "request_duration_seconds": "TODO",
        "active_connections": "TODO"
    }


if __name__ == "__main__":
    settings = get_settings()
    
    # Configurar logging para desenvolvimento
    if settings.environment == "development":
        logging.basicConfig(level=logging.INFO)
    
    logger.info("Iniciando servidor", 
               host=settings.host, 
               port=settings.port,
               environment=settings.environment)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )


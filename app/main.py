from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .core.config import settings
from .core.database import engine, Base
from .core.exceptions import LeviticaException
from app.api.v1 import router as api_router
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.APP_VERSION,
#     description="Levitica OneHealth Platform API",
#     docs_url="/api/docs" if settings.DEBUG else None,
#     redoc_url="/api/redoc" if settings.DEBUG else None,
#     openapi_url="/api/openapi.json" if settings.DEBUG else None
# )

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Levitica OneHealth Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware - Use the property to get list
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - Time: {process_time:.3f}s")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(LeviticaException)
async def levitica_exception_handler(request: Request, exc: LeviticaException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.error_code,
            "data": exc.data
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append(f"{error['loc'][-1]}: {error['msg']}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors,
            "error_code": "VALIDATION_ERROR"
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": "HTTP_ERROR"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR"
        }
    )


# Include API router
app.include_router(api_router)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs" if settings.DEBUG else None,
        "health": "/health"
    }


# Database initialization
# @app.on_event("startup")
# async def startup():
#     logger.info("Starting up Levitica OneHealth API")
#     try:
#         # Create tables
#         Base.metadata.create_all(bind=engine)
#         logger.info("Database tables created/verified")
#     except Exception as e:
#         logger.error(f"Database initialization error: {str(e)}")
@app.on_event("startup")
async def startup():
    logger.info("Starting up Levitica OneHealth API")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
 

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down Levitica OneHealth API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
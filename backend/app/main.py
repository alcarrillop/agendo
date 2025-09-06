"""
Main FastAPI application for Agendo backend.
Handles all API endpoints for the conversational agent system.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.database.connection import DatabaseManager, get_async_db
from app.services.webhook_manager import webhook_manager
from app.services.env_watcher import start_env_watcher, stop_env_watcher
from app.api.webhooks import router as webhooks_router
from app.api.evolution import router as evolution_router
from app.api.agent import router as agent_router
from app.api.agent_configs import router as agent_configs_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting Awendo Backend...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    try:
        # Initialize database
        await DatabaseManager.init_database()
        logger.info("✅ Database initialized successfully")
        
        # Initialize and update webhooks
        await initialize_webhooks()
        
        # Start environment file watcher (optional - only if watchdog is available)
        try:
            await start_env_watcher()
            logger.info("👀 Environment file watcher started")
        except ImportError:
            logger.info("ℹ️  Environment file watcher not available (watchdog not installed)")
        except Exception as e:
            logger.warning(f"⚠️  Could not start environment file watcher: {e}")
        
        # Log configuration status
        log_configuration_status()
        
        logger.info("🎉 Awendo Backend started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Awendo Backend...")
    try:
        # Stop environment file watcher
        try:
            await stop_env_watcher()
            logger.info("🛑 Environment file watcher stopped")
        except Exception as e:
            logger.warning(f"Warning stopping env watcher: {e}")
        
        await DatabaseManager.close_connections()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("👋 Awendo Backend shutdown complete")


async def initialize_webhooks():
    """Initialize and update webhooks for all instances."""
    try:
        if not settings.WEBHOOK_BASE_URL:
            logger.warning("⚠️  WEBHOOK_BASE_URL not configured - webhooks disabled")
            return
        
        logger.info("🔗 Initializing webhooks...")
        
        # Get database session
        async for db in get_async_db():
            result = await webhook_manager.update_all_webhooks(db)
            break
            
            if result.get("success"):
                logger.info(f"✅ Webhooks initialized: {result.get('updated_count')}/{result.get('total_count')} instances")
            else:
                logger.warning(f"⚠️  Webhook initialization completed with issues: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"❌ Error initializing webhooks: {e}")


def log_configuration_status():
    """Log the configuration status of external services."""
    logger.info("📊 Configuration Status:")
    
    # Evolution API
    if settings.EVOLUTION_API_URL:
        logger.info("✅ Evolution API: Configured")
    else:
        logger.warning("⚠️  Evolution API: Not configured")
    
    # Webhook URL
    if settings.WEBHOOK_BASE_URL:
        logger.info("✅ Webhook URL: Configured")
    else:
        logger.warning("⚠️  Webhook URL: Not configured")
    
    # Google Calendar
    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
        logger.info("✅ Google Calendar: Configured")
    else:
        logger.warning("⚠️  Google Calendar: Not configured")
    
    # OpenAI
    if settings.OPENAI_API_KEY:
        logger.info("✅ OpenAI API: Configured")
    else:
        logger.warning("⚠️  OpenAI API: Not configured")
    
    # Database
    if settings.SUPABASE_URL or settings.DATABASE_URL:
        logger.info("✅ Database: Configured")
    else:
        logger.warning("⚠️  Database: Using SQLite fallback")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Awendo - Conversational WhatsApp agent with appointment booking",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests for debugging."""
    if settings.DEBUG:
        logger.info(f"📥 {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    if settings.DEBUG:
        logger.info(f"📤 {request.method} {request.url.path} - {response.status_code}")
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions gracefully."""
    logger.error(f"🚨 Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Include API routers
from app.api.instances import router as instances_router
from app.api.webhook_management import router as webhook_management_router
app.include_router(webhooks_router, prefix=settings.API_V1_STR)
app.include_router(evolution_router, prefix=settings.API_V1_STR)
app.include_router(agent_router, prefix=settings.API_V1_STR)
app.include_router(agent_configs_router, prefix=settings.API_V1_STR)
app.include_router(instances_router, prefix=settings.API_V1_STR)
app.include_router(webhook_management_router, prefix=settings.API_V1_STR)


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "message": "Awendo Backend API is running!"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",  # This would be current timestamp
        "version": settings.APP_VERSION,
        "services": {
            "database": "connected",  # This would check actual database connection
            "evolution_api": "configured" if settings.EVOLUTION_API_URL else "not_configured",
            "google_calendar": "configured" if settings.GOOGLE_CLIENT_ID else "not_configured",
            "openai": "configured" if settings.OPENAI_API_KEY else "not_configured"
        }
    }


@app.get(f"{settings.API_V1_STR}/status")
async def api_status():
    """Detailed API status endpoint."""
    return {
        "api": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": "development" if settings.DEBUG else "production",
            "cors_origins": settings.BACKEND_CORS_ORIGINS
        },
        "integrations": {
            "evolution_api": {
                "configured": bool(settings.EVOLUTION_API_URL),
                "url": settings.EVOLUTION_API_URL[:50] + "..." if settings.EVOLUTION_API_URL else None
            },
            "google_calendar": {
                "configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)
            },
            "openai": {
                "configured": bool(settings.OPENAI_API_KEY)
            },
            "database": {
                "type": "postgresql" if settings.SUPABASE_URL or settings.DATABASE_URL else "sqlite",
                "configured": bool(settings.SUPABASE_URL or settings.DATABASE_URL)
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

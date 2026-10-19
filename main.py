from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from core.module_registry import ModuleRegistry
from core.config import settings
from core.database import create_all_tables
from core.rate_limit import RateLimitMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 AITools Platform starting...")

    # Création des tables DB (idempotent — sans effet si elles existent déjà)
    await create_all_tables()
    logger.info("✅ Base de données prête")

    registry = ModuleRegistry(app)
    registry.autodiscover()
    logger.info(f"✅ {len(registry.modules)} module(s) loaded")
    yield
    # Shutdown
    logger.info("👋 AITools Platform shutting down...")


app = FastAPI(
    title="AITools Platform",
    description="Plateforme d'outils IA open-source — Un jour, un script Python",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — autoriser Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting — 10 traitements/min par utilisateur ou IP
app.add_middleware(RateLimitMiddleware, redis_url=settings.REDIS_URL)


@app.get("/", tags=["health"])
async def root():
    return {
        "name": "AITools Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.health import router as health_router
from app.api.analyze import router as analyze_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint (as per api-specification.md: GET /api/health)
app.include_router(health_router, prefix="/api", tags=["Health"])

# Analyze endpoint (as per api-specification.md: POST /api/v1/analyze)
app.include_router(analyze_router, prefix=settings.API_V1_STR, tags=["Analyze"])

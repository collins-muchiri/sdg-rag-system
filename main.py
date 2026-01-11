from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

from config.settings import settings
from src.api.routers import documents, search, sdg, transportation
from src.core.database import init_db
from src.core.vector_store import init_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await init_vector_store()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="SDG RAG System",
    description="AI-powered file management and search system for UN/UN Habitat SDG documents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(sdg.router, prefix="/api/v1/sdg", tags=["sdg"])
app.include_router(transportation.router, prefix="/api/v1/transportation", tags=["transportation"])


@app.get("/")
async def root():
    return {
        "message": "SDG RAG System API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "vector_store": "ready"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.config import engine
from backend.database.models import Base
from backend.routers import debate
from backend.routers import debate_stream


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="MindColiseum API",
    description="AI Debate Platform - Witness AI agents debate any topic",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(debate.router)
app.include_router(debate_stream.router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "app": "MindColiseum",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """API health check."""
    return {"status": "healthy"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_prompts import router as prompts_router
from app.api.routes_analysis import router as analysis_router
from app.api.routes_history import router as history_router
from app.database import Base, engine
from app.seed import seed_database

# Create SQLite tables
Base.metadata.create_all(bind=engine)

# Seed initial presets if db is empty
seed_database()

app = FastAPI(
    title="Sound Machina API",
    description="Deterministic neural music composition engine and prompt generator",
    version="0.3.2"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local MVP development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(prompts_router)
app.include_router(analysis_router)
app.include_router(history_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Sound Machina Engine",
        "version": "0.3.2",
        "api_schema": "v1"
    }

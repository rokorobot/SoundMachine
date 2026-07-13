import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import database
from app.migrations import run_migrations
from app.seed import seed_if_empty
from app.errors import install_error_handlers
from app.api.routes_prompts import router as prompts_router
from app.api.routes_analysis import router as analysis_router
from app.api.routes_history import router as history_router

APP_VERSION = "0.4.0"


def initialize():
    """Resolve the DB (C2/R32), run additive migrations behind the backup gate
    (R31), and seed presets if empty. Called at startup; never at import."""
    engine = database.configure()
    run_migrations(engine, db_path=database.DB_PATH, backup=True)
    seed_if_empty(database.SessionLocal)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize()
    yield


def _cors_origins():
    raw = os.environ.get("SOUND_MACHINA_CORS_ORIGINS")
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return ["http://localhost:3000", "http://127.0.0.1:3000"]


def create_app() -> FastAPI:
    app = FastAPI(
        title="Sound Machina API",
        description="Deterministic neural music composition lifecycle engine",
        version=APP_VERSION,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)
    app.include_router(prompts_router)
    app.include_router(analysis_router)
    app.include_router(history_router)

    @app.get("/")
    def read_root():
        return {"status": "online", "service": "Sound Machina Engine",
                "version": APP_VERSION, "api_schema": "v1"}

    return app


app = create_app()

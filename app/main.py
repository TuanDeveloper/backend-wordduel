import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.db.database import engine
from app.db.seed import run_seed_if_empty
from app.dependencies.database import get_db
from app.routers.api import api_router
from app.routers.rooms import handle_websocket_connection
from app.websockets.connection_manager import manager

logger = logging.getLogger(__name__)
CURRENT_SCHEMA_REVISION = "943c0ad1f6e2"


def _assert_schema_current(connection) -> None:
    revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
    if revision != CURRENT_SCHEMA_REVISION:
        raise RuntimeError("Database schema is not current; run 'alembic upgrade head' before serving traffic")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Do not start serving if the required database is unavailable or seeding fails.
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            _assert_schema_current(connection)
        run_seed_if_empty()
    except Exception:
        logger.exception("Application startup check failed")
        raise
    try:
        yield
    finally:
        await manager.shutdown()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
register_exception_handlers(app)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to WordDuel API"}


@app.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
def readiness() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            _assert_schema_current(connection)
    except Exception as exc:
        logger.warning("Readiness check failed", exc_info=True)
        raise HTTPException(status_code=503, detail="Database or migrations are not ready") from exc
    return {"status": "ready"}


@app.websocket("/ws/{code}")
async def ws_room(websocket: WebSocket, code: str, db: Session = Depends(get_db)) -> None:
    await handle_websocket_connection(websocket, code, db)

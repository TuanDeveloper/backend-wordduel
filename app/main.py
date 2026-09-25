from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.api import api_router
from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.db.seed import run_seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tu dong seed du lieu mau khi khoi dong neu database chua co bo tu nao
    try:
        run_seed_if_empty()
    except Exception as e:
        print(f"[Auto-Seed] Startup seed failed: {e}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Register custom exception handlers
register_exception_handlers(app)


from fastapi import WebSocket, Depends
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.routers.rooms import handle_websocket_connection


@app.get("/")
def root():
    return {"message": "Welcome to WordDuel API"}


@app.websocket("/ws/{code}")
async def ws_room(websocket: WebSocket, code: str, db: Session = Depends(get_db)):
    await handle_websocket_connection(websocket, code, db)

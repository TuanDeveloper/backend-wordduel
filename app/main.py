from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.api import api_router
from app.core.config import settings
from app.core.handlers import register_exception_handlers

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
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


@app.get("/")
def root():
    return {"message": "Welcome to WordDuel API"}

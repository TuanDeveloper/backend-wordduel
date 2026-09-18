from fastapi import APIRouter
from app.routers import words, auth, rooms

api_router = APIRouter()
api_router.include_router(words.router, tags=["words"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])

from fastapi import APIRouter

from app.api.routes.diagnosis import router as diagnosis_router

api_router = APIRouter()
api_router.include_router(diagnosis_router)

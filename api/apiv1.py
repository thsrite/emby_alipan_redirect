from fastapi import APIRouter

from api import alipan

api_router = APIRouter()
api_router.include_router(alipan.router, prefix="/alipan", tags=["alipan"])

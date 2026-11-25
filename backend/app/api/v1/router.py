
"""Aggregate API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints.dataset import router as dataset_router
from app.api.v1.endpoints.eda import router as eda_router
from app.api.v1.endpoints.recommendations import router as recommendations_router
from app.api.v1.endpoints.preprocessing import router as preprocessing_router
from app.api.v1.endpoints.export import router as export_router

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(dataset_router)
api_v1_router.include_router(eda_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(preprocessing_router)
api_v1_router.include_router(export_router)

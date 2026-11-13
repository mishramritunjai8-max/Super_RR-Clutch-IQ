"""
SUPER RR — CLUTCH IQ
Health and Metadata Routes
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from backend.api.dependencies import get_data_service
from backend.api.services.data_service import DataService

router = APIRouter(tags=["Health & Metadata"])


@router.get("/health", summary="Health Check", description="Returns API status, version, and essential dataset availability.")
def get_health(data_service: DataService = Depends(get_data_service)) -> Dict[str, Any]:
    return data_service.get_health_status()


@router.get("/metadata", summary="Application Metadata", description="Returns tournament seasons, formats, counts, pressure categories, and ML engine versions.")
def get_metadata(data_service: DataService = Depends(get_data_service)) -> Dict[str, Any]:
    return data_service.get_metadata()

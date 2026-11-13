"""
SUPER RR — CLUTCH IQ
FastAPI Router: Macro Analytics & Pressure Segments
"""

from fastapi import APIRouter, Depends
from backend.api.dependencies import get_data_service
from backend.api.services.data_service import DataService
from backend.api.schemas.analytics import AnalyticsSummaryResponse, PressureAnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Macro Analytics"])


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Get Macro Dataset Analytics Summary",
    description=(
        "Returns comprehensive macro-level dataset totals, including total and completed matches, "
        "deliveries (regular vs quarantined Super Overs), team vs batter runs, extras reconciliation, "
        "total bowler wickets, unique player counts, and pressure vs baseline breakdown."
    )
)
def get_analytics_summary(
    service: DataService = Depends(get_data_service)
) -> AnalyticsSummaryResponse:
    return service.get_analytics_summary()


@router.get(
    "/pressure",
    response_model=PressureAnalyticsResponse,
    summary="Get Pressure Segment Analytics & Run Algebra",
    description=(
        "Returns delivery-level statistics, boundary percentages, strike rates, economy rates, "
        "and dot percentages across all 8 segmented environments (Overall Regular, Baseline, "
        "Death Overs, Close Chases, Knockouts, and Deduplicated Any-Pressure Union). "
        "Includes methodological clarification on set algebra and Super Over isolation."
    )
)
def get_pressure_analytics(
    service: DataService = Depends(get_data_service)
) -> PressureAnalyticsResponse:
    return service.get_pressure_analytics()

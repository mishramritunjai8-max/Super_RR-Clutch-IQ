"""
SUPER RR — CLUTCH IQ
Archetype API Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, HTTPException
from backend.api.dependencies import get_data_service, paginate
from backend.api.services.data_service import DataService
from backend.api.schemas.archetype import (
    BattingArchetypeProfile,
    BowlingArchetypeProfile,
    BattingArchetypeDetail,
    BowlingArchetypeDetail
)
from backend.api.schemas.common import PaginatedResponse

router = APIRouter(prefix="/archetypes", tags=["Archetypes"])


@router.get(
    "/batting",
    response_model=List[BattingArchetypeProfile],
    summary="List All Batting Archetypes",
    description="Returns summary statistics, centroid values, strengths, weaknesses, and tactical roles for all 3 batting archetypes."
)
def list_batting_archetypes(data_service: DataService = Depends(get_data_service)):
    profiles = data_service.get_batting_archetypes()
    return [BattingArchetypeProfile(**p) for p in profiles]


@router.get(
    "/bowling",
    response_model=List[BowlingArchetypeProfile],
    summary="List All Bowling Archetypes",
    description="Returns summary statistics, centroid values, strengths, weaknesses, and tactical roles for all 3 bowling archetypes."
)
def list_bowling_archetypes(data_service: DataService = Depends(get_data_service)):
    profiles = data_service.get_bowling_archetypes()
    return [BowlingArchetypeProfile(**p) for p in profiles]


@router.get(
    "/batting/{cluster_id}",
    response_model=BattingArchetypeDetail,
    summary="Get Batting Archetype with Players",
    description="Returns a specific batting archetype profile and a paginated list of all assigned players (sorted by Clutch IQ)."
)
def get_batting_archetype_detail(
    cluster_id: int = Path(..., ge=0, description="Numerical cluster ID (0, 1, or 2)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cohort: Optional[str] = Query(None, pattern="^(primary|emerging)$", description="Filter by cohort"),
    data_service: DataService = Depends(get_data_service)
):
    detail = data_service.get_batting_archetype_detail(cluster_id)
    if not detail:
        raise HTTPException(
            status_code=404,
            detail=f"Batting cluster with ID {cluster_id} not found. Valid cluster IDs: [0, 1, 2]"
        )
    profile, players = detail
    
    if cohort:
        players = [p for p in players if p["cohort"] == cohort.lower()]
        
    page_items, pagination = paginate(players, page=page, page_size=page_size)
    return BattingArchetypeDetail(
        profile=BattingArchetypeProfile(**profile),
        players=PaginatedResponse(items=page_items, pagination=pagination)
    )


@router.get(
    "/bowling/{cluster_id}",
    response_model=BowlingArchetypeDetail,
    summary="Get Bowling Archetype with Players",
    description="Returns a specific bowling archetype profile and a paginated list of all assigned players (sorted by Clutch IQ)."
)
def get_bowling_archetype_detail(
    cluster_id: int = Path(..., ge=0, description="Numerical cluster ID (0, 1, or 2)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cohort: Optional[str] = Query(None, pattern="^(primary|emerging)$", description="Filter by cohort"),
    data_service: DataService = Depends(get_data_service)
):
    detail = data_service.get_bowling_archetype_detail(cluster_id)
    if not detail:
        raise HTTPException(
            status_code=404,
            detail=f"Bowling cluster with ID {cluster_id} not found. Valid cluster IDs: [0, 1, 2]"
        )
    profile, players = detail
    
    if cohort:
        players = [p for p in players if p["cohort"] == cohort.lower()]
        
    page_items, pagination = paginate(players, page=page, page_size=page_size)
    return BowlingArchetypeDetail(
        profile=BowlingArchetypeProfile(**profile),
        players=PaginatedResponse(items=page_items, pagination=pagination)
    )

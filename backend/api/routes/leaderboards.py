"""
SUPER RR — CLUTCH IQ
Leaderboard API Routes
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from backend.api.dependencies import get_data_service, paginate
from backend.api.services.data_service import DataService
from backend.api.schemas.common import PaginatedResponse
from backend.api.schemas.leaderboard import BatterLeaderboardItem, BowlerLeaderboardItem

router = APIRouter(prefix="/leaderboards", tags=["Leaderboards"])

VALID_BATTING_SORT_FIELDS = {
    "clutch_iq", "primary_rank", "strike_rate", "balls_faced", "total_runs",
    "batting_average", "raw_delta_strike_rate", "match_count", "dot_ball_pct", "boundary_ball_pct"
}

VALID_BOWLING_SORT_FIELDS = {
    "clutch_iq", "primary_rank", "economy_rate", "legal_balls", "runs_conceded",
    "bowler_wickets", "bowling_strike_rate", "raw_delta_economy", "match_count",
    "dot_ball_pct", "boundary_balls_conceded_per_100_legal_balls"
}


@router.get(
    "/batters",
    response_model=PaginatedResponse[BatterLeaderboardItem],
    summary="Batting Clutch IQ Leaderboard",
    description="Returns the approved Phase 3 batting leaderboard sorted by Clutch IQ (default) with pagination, search, and metric filtering."
)
def get_batting_leaderboard(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(None, description="Case-insensitive player name search"),
    min_balls: Optional[int] = Query(None, ge=1, description="Minimum pressure balls faced"),
    min_matches: Optional[int] = Query(None, ge=1, description="Minimum distinct pressure matches"),
    cohort: str = Query("primary", pattern="^(primary|emerging|all)$", description="Filter by cohort ('primary', 'emerging', 'all')"),
    sort_by: str = Query("clutch_iq", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction ('asc' or 'desc')"),
    data_service: DataService = Depends(get_data_service)
):
    if sort_by not in VALID_BATTING_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by field '{sort_by}'. Supported fields: {sorted(list(VALID_BATTING_SORT_FIELDS))}"
        )
        
    all_batters = data_service.get_batters_leaderboard(
        search=search,
        min_balls=min_balls,
        min_matches=min_matches,
        cohort=cohort if cohort != "all" else None,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    page_items, pagination = paginate(all_batters, page=page, page_size=page_size)
    return PaginatedResponse(items=page_items, pagination=pagination)


@router.get(
    "/bowlers",
    response_model=PaginatedResponse[BowlerLeaderboardItem],
    summary="Bowling Clutch IQ Leaderboard",
    description="Returns the approved Phase 3 bowling leaderboard sorted by Clutch IQ (default) with pagination, search, and metric filtering."
)
def get_bowling_leaderboard(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(None, description="Case-insensitive player name search"),
    min_balls: Optional[int] = Query(None, ge=1, description="Minimum legal pressure balls bowled"),
    min_matches: Optional[int] = Query(None, ge=1, description="Minimum distinct pressure matches"),
    cohort: str = Query("primary", pattern="^(primary|emerging|all)$", description="Filter by cohort ('primary', 'emerging', 'all')"),
    sort_by: str = Query("clutch_iq", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction ('asc' or 'desc')"),
    data_service: DataService = Depends(get_data_service)
):
    if sort_by not in VALID_BOWLING_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by field '{sort_by}'. Supported fields: {sorted(list(VALID_BOWLING_SORT_FIELDS))}"
        )
        
    all_bowlers = data_service.get_bowlers_leaderboard(
        search=search,
        min_balls=min_balls,
        min_matches=min_matches,
        cohort=cohort if cohort != "all" else None,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    page_items, pagination = paginate(all_bowlers, page=page, page_size=page_size)
    return PaginatedResponse(items=page_items, pagination=pagination)

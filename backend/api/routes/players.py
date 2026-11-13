"""
SUPER RR — CLUTCH IQ
Player Profile & Comparison API Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from backend.api.dependencies import get_data_service
from backend.api.services.data_service import DataService
from backend.api.schemas.player import (
    PlayerSummary,
    PlayerBattingProfile,
    PlayerBowlingProfile,
    PlayerComparisonItem,
    PlayerComparisonResponse
)

router = APIRouter(prefix="/players", tags=["Players"])


@router.get(
    "/compare",
    response_model=PlayerComparisonResponse,
    summary="Compare Multiple Players",
    description="Compares 2 to 5 players side-by-side using player IDs, displaying their batting and bowling pressure profiles."
)
def compare_players(
    player_ids: str = Query(..., description="Comma-separated player IDs (e.g., '20702,8,781')"),
    data_service: DataService = Depends(get_data_service)
):
    try:
        raw_ids = [int(pid.strip()) for pid in player_ids.split(",") if pid.strip()]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid player_ids format. Must be a comma-separated list of integers."
        )
        
    # Deduplicate while preserving order
    seen = set()
    parsed_ids = []
    for pid in raw_ids:
        if pid not in seen:
            seen.add(pid)
            parsed_ids.append(pid)
        
    if len(parsed_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 distinct player IDs are required for comparison."
        )
    if len(parsed_ids) > 5:
        raise HTTPException(
            status_code=400,
            detail="A maximum of 5 players can be compared in a single request."
        )
        
    comparison_items = []
    for pid in parsed_ids:
        summary = data_service.get_player_summary(pid)
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"Player with ID {pid} not found in player registry."
            )
            
        bat_profile = data_service.get_player_batting_profile(pid)
        bowl_profile = data_service.get_player_bowling_profile(pid)
        
        comparison_items.append(
            PlayerComparisonItem(
                player_id=pid,
                player_name=summary["player_name"],
                teams=summary.get("teams", []),
                batting=PlayerBattingProfile(**bat_profile) if bat_profile else None,
                bowling=PlayerBowlingProfile(**bowl_profile) if bowl_profile else None
            )
        )
        
    return PlayerComparisonResponse(
        players=comparison_items,
        compared_count=len(comparison_items)
    )


@router.get(
    "/{player_id}",
    response_model=PlayerSummary,
    summary="Get Player Summary",
    description="Returns high-level player profile, team associations, and availability of pressure batting and bowling records."
)
def get_player(
    player_id: int = Path(..., ge=1, description="Unique player identifier"),
    data_service: DataService = Depends(get_data_service)
):
    player = data_service.get_player_summary(player_id)
    if not player:
        raise HTTPException(
            status_code=404,
            detail=f"Player with ID {player_id} not found."
        )
    return PlayerSummary(**player)


@router.get(
    "/{player_id}/batting",
    response_model=PlayerBattingProfile,
    summary="Get Player Batting Profile",
    description="Returns detailed pressure batting metrics, baseline comparison, regularized deltas, Clutch IQ, and archetype assignment."
)
def get_player_batting(
    player_id: int = Path(..., ge=1, description="Unique player identifier"),
    data_service: DataService = Depends(get_data_service)
):
    # Verify player exists first
    summary = data_service.get_player_summary(player_id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"Player with ID {player_id} not found."
        )
        
    bat_profile = data_service.get_player_batting_profile(player_id)
    if not bat_profile:
        raise HTTPException(
            status_code=404,
            detail=f"No pressure batting profile found for player {summary['player_name']} (ID: {player_id})."
        )
    return PlayerBattingProfile(**bat_profile)


@router.get(
    "/{player_id}/bowling",
    response_model=PlayerBowlingProfile,
    summary="Get Player Bowling Profile",
    description="Returns detailed pressure bowling metrics, baseline comparison, regularized deltas, Clutch IQ, and archetype assignment."
)
def get_player_bowling(
    player_id: int = Path(..., ge=1, description="Unique player identifier"),
    data_service: DataService = Depends(get_data_service)
):
    summary = data_service.get_player_summary(player_id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"Player with ID {player_id} not found."
        )
        
    bowl_profile = data_service.get_player_bowling_profile(player_id)
    if not bowl_profile:
        raise HTTPException(
            status_code=404,
            detail=f"No pressure bowling profile found for player {summary['player_name']} (ID: {player_id})."
        )
        
    bowl_profile = data_service.get_player_bowling_profile(player_id)
    if not bowl_profile:
        raise HTTPException(
            status_code=404,
            detail=f"Player {summary['player_name']} (ID: {player_id}) has no recorded pressure bowling data."
        )
    return PlayerBowlingProfile(**bowl_profile)

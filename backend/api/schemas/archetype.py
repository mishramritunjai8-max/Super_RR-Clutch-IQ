"""
SUPER RR — CLUTCH IQ
Archetype Pydantic Schemas
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from backend.api.schemas.common import PaginatedResponse
from backend.api.schemas.leaderboard import BatterLeaderboardItem, BowlerLeaderboardItem


class BattingArchetypeProfile(BaseModel):
    cluster_id: int = Field(..., description="Numerical cluster ID (0, 1, 2)")
    archetype_name: str = Field(..., description="Descriptive archetype persona name")
    primary_player_count: int = Field(..., description="Number of primary players in this cluster")
    emerging_player_count: int = Field(..., description="Number of emerging players in this cluster")
    total_player_count: int = Field(..., description="Total players assigned to this cluster")
    mean_pressure_strike_rate: float = Field(..., description="Mean pressure strike rate")
    median_pressure_strike_rate: float = Field(..., description="Median pressure strike rate")
    std_pressure_strike_rate: float = Field(..., description="Standard deviation of strike rate")
    mean_raw_delta_strike_rate: float = Field(..., description="Mean strike rate delta over regularized baseline")
    median_raw_delta_strike_rate: float = Field(..., description="Median strike rate delta")
    mean_dot_ball_pct: float = Field(..., description="Mean dot-ball percentage")
    median_dot_ball_pct: float = Field(..., description="Median dot-ball percentage")
    mean_boundary_ball_pct: float = Field(..., description="Mean boundary ball percentage")
    median_boundary_ball_pct: float = Field(..., description="Median boundary ball percentage")
    mean_batting_avg_imputed: float = Field(..., description="Mean batting average")
    median_batting_avg_imputed: float = Field(..., description="Median batting average")
    mean_clutch_iq: float = Field(..., description="Mean Clutch IQ score (for external reference)")
    median_clutch_iq: float = Field(..., description="Median Clutch IQ score")
    representative_players: List[str] = Field(..., description="List of notable representative players")
    strengths: str = Field(..., description="Empirical performance strengths")
    weaknesses: str = Field(..., description="Empirical performance vulnerabilities")
    distinguishing_characteristics: str = Field(..., description="Statistical hallmarks distinguishing this cluster")
    potential_tactical_role: str = Field(..., description="Potential tactical scouting profile")


class BowlingArchetypeProfile(BaseModel):
    cluster_id: int = Field(..., description="Numerical cluster ID (0, 1, 2)")
    archetype_name: str = Field(..., description="Descriptive archetype persona name")
    primary_player_count: int = Field(..., description="Number of primary players in this cluster")
    emerging_player_count: int = Field(..., description="Number of emerging players in this cluster")
    total_player_count: int = Field(..., description="Total players assigned to this cluster")
    mean_pressure_economy: float = Field(..., description="Mean pressure economy rate")
    median_pressure_economy: float = Field(..., description="Median pressure economy rate")
    std_pressure_economy: float = Field(..., description="Standard deviation of economy rate")
    mean_raw_delta_economy: float = Field(..., description="Mean economy delta (positive = improvement)")
    median_raw_delta_economy: float = Field(..., description="Median economy delta")
    mean_wickets_per_100_balls: float = Field(..., description="Mean wickets taken per 100 legal balls")
    mean_dot_ball_pct: float = Field(..., description="Mean dot-ball percentage")
    median_dot_ball_pct: float = Field(..., description="Median dot-ball percentage")
    mean_boundary_balls_per_100: float = Field(..., description="Mean boundaries conceded per 100 legal balls")
    median_boundary_balls_per_100: float = Field(..., description="Median boundaries conceded per 100 legal balls")
    mean_clutch_iq: float = Field(..., description="Mean Clutch IQ score (for external reference)")
    median_clutch_iq: float = Field(..., description="Median Clutch IQ score")
    representative_players: List[str] = Field(..., description="List of notable representative players")
    strengths: str = Field(..., description="Empirical performance strengths")
    weaknesses: str = Field(..., description="Empirical performance vulnerabilities")
    distinguishing_characteristics: str = Field(..., description="Statistical hallmarks distinguishing this cluster")
    potential_tactical_role: str = Field(..., description="Potential tactical scouting profile")


class BattingArchetypeDetail(BaseModel):
    profile: BattingArchetypeProfile = Field(..., description="Archetype summary profile")
    players: PaginatedResponse[BatterLeaderboardItem] = Field(..., description="Paginated list of assigned players")


class BowlingArchetypeDetail(BaseModel):
    profile: BowlingArchetypeProfile = Field(..., description="Archetype summary profile")
    players: PaginatedResponse[BowlerLeaderboardItem] = Field(..., description="Paginated list of assigned players")

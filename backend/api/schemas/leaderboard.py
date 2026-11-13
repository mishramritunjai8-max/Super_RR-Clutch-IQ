"""
SUPER RR — CLUTCH IQ
Leaderboard Pydantic Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class BatterLeaderboardItem(BaseModel):
    player_id: int = Field(..., description="Unique player identifier")
    player_name: str = Field(..., description="Full player name")
    rank: Optional[int] = Field(None, description="Primary cohort rank (1-10 for marquee, up to 249 for primary)")
    clutch_iq: float = Field(..., description="Standardized Bayesian Clutch IQ score [0, 100]")
    cohort: str = Field(..., description="Cohort classification ('primary' >= 50 balls, 'emerging' < 50 balls)")
    assignment_status: str = Field(..., description="Archetype assignment status ('fitted' or 'provisional')")
    archetype_name: str = Field(..., description="Phase 4 empirical cricket archetype")
    balls_faced: int = Field(..., description="Total pressure balls faced (excluding wides)")
    match_count: int = Field(..., description="Number of distinct pressure matches")
    total_runs: int = Field(..., description="Total runs scored off the bat under pressure")
    strike_rate: float = Field(..., description="Observed pressure strike rate (runs per 100 balls)")
    batting_average: Optional[float] = Field(None, description="Observed pressure batting average (null if zero dismissals)")
    raw_delta_strike_rate: float = Field(..., description="Unweighted strike rate elevation over baseline")
    dot_ball_pct: float = Field(..., description="Percentage of pressure balls resulting in zero runs")
    boundary_ball_pct: float = Field(..., description="Percentage of pressure balls hit for four or six")
    reliability_weight: float = Field(..., description="Bayesian credibility shrinkage weight [0, 1]")


class BowlerLeaderboardItem(BaseModel):
    player_id: int = Field(..., description="Unique player identifier")
    player_name: str = Field(..., description="Full player name")
    rank: Optional[int] = Field(None, description="Primary cohort rank (1-10 for marquee, up to 219 for primary)")
    clutch_iq: float = Field(..., description="Standardized Bayesian Clutch IQ score [0, 100]")
    cohort: str = Field(..., description="Cohort classification ('primary' >= 50 legal balls, 'emerging' < 50)")
    assignment_status: str = Field(..., description="Archetype assignment status ('fitted' or 'provisional')")
    archetype_name: str = Field(..., description="Phase 4 empirical cricket archetype")
    legal_balls: int = Field(..., description="Total legal pressure balls bowled")
    match_count: int = Field(..., description="Number of distinct pressure matches")
    runs_conceded: int = Field(..., description="Total bowler runs conceded under pressure")
    bowler_wickets: int = Field(..., description="Total bowler-creditable wickets taken under pressure")
    economy_rate: float = Field(..., description="Observed pressure economy rate (runs per 6 legal balls)")
    bowling_strike_rate: Optional[float] = Field(None, description="Observed balls per wicket (null if zero wickets)")
    bowling_average: Optional[float] = Field(None, description="Observed runs per wicket (null if zero wickets)")
    raw_delta_economy: float = Field(..., description="Signed economy improvement (baseline - pressure; positive = better)")
    dot_ball_pct: float = Field(..., description="Percentage of legal pressure deliveries conceding zero runs")
    boundary_balls_conceded_per_100_legal_balls: float = Field(..., description="Boundaries conceded per 100 legal balls")
    reliability_weight: float = Field(..., description="Bayesian credibility shrinkage weight [0, 1]")

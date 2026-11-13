"""
SUPER RR — CLUTCH IQ
Player Profile & Comparison Pydantic Schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PlayerSummary(BaseModel):
    player_id: int = Field(..., description="Unique player identifier")
    player_name: str = Field(..., description="Full player name")
    teams: List[str] = Field(default_factory=list, description="Associated franchise / national teams")
    competitions: List[str] = Field(default_factory=list, description="Competitions in which player competed")
    has_batting_profile: bool = Field(..., description="True if player has pressure batting data")
    has_bowling_profile: bool = Field(..., description="True if player has pressure bowling data")
    batting_clutch_iq: Optional[float] = Field(None, description="Batting Clutch IQ score [0, 100]")
    bowling_clutch_iq: Optional[float] = Field(None, description="Bowling Clutch IQ score [0, 100]")
    batting_rank: Optional[int] = Field(None, description="Primary batting rank if eligible")
    bowling_rank: Optional[int] = Field(None, description="Primary bowling rank if eligible")
    batting_archetype: Optional[str] = Field(None, description="Batting archetype persona")
    bowling_archetype: Optional[str] = Field(None, description="Bowling archetype persona")
    batting_cohort: Optional[str] = Field(None, description="'primary' or 'emerging'")
    bowling_cohort: Optional[str] = Field(None, description="'primary' or 'emerging'")
    batting_assignment_status: Optional[str] = Field(None, description="'fitted' or 'provisional'")
    bowling_assignment_status: Optional[str] = Field(None, description="'fitted' or 'provisional'")


class PlayerBattingProfile(BaseModel):
    player_id: int = Field(..., description="Unique player identifier")
    player_name: str = Field(..., description="Full player name")
    teams: List[str] = Field(default_factory=list, description="Teams")
    competitions: List[str] = Field(default_factory=list, description="Competitions")
    clutch_iq: float = Field(..., description="Bayesian Clutch IQ score [0, 100]")
    rank: Optional[int] = Field(None, description="Primary cohort rank (1 to 249)")
    cohort: str = Field(..., description="'primary' (>= 50 balls) or 'emerging' (< 50)")
    assignment_status: str = Field(..., description="'fitted' or 'provisional'")
    archetype_name: str = Field(..., description="Phase 4 empirical cricket archetype")
    player_archetype_explanation: str = Field(..., description="Player-level archetype narrative")
    
    # Pressure Metrics
    balls_faced: int = Field(..., description="Pressure balls faced")
    total_runs: int = Field(..., description="Pressure runs off bat")
    dismissals: int = Field(..., description="Pressure dismissals")
    not_outs: int = Field(..., description="Pressure not outs")
    innings_count: int = Field(..., description="Pressure innings count")
    match_count: int = Field(..., description="Distinct pressure matches")
    strike_rate: float = Field(..., description="Pressure strike rate")
    batting_average: Optional[float] = Field(None, description="Pressure batting average (null if 0 dismissals)")
    dot_ball_pct: float = Field(..., description="Pressure dot-ball %")
    boundary_ball_pct: float = Field(..., description="Pressure boundary ball %")
    fours: int = Field(..., description="Pressure fours")
    sixes: int = Field(..., description="Pressure sixes")
    
    # Baseline Metrics
    balls_baseline: Optional[int] = Field(None, description="Baseline balls faced")
    runs_baseline: Optional[int] = Field(None, description="Baseline runs scored")
    sr_baseline: Optional[float] = Field(None, description="Baseline strike rate")
    avg_baseline: Optional[float] = Field(None, description="Baseline batting average")
    dot_pct_baseline: Optional[float] = Field(None, description="Baseline dot-ball %")
    boundary_pct_baseline: Optional[float] = Field(None, description="Baseline boundary ball %")
    
    # Regularized & Shrunk Deltas
    reg_sr_base: float = Field(..., description="Regularized baseline strike rate (empirical Bayes)")
    raw_delta_strike_rate: float = Field(..., description="Raw delta SR over regularized baseline")
    shrunk_delta_strike_rate: float = Field(..., description="Bayesian credibility-shrunk delta SR")
    reliability_weight: float = Field(..., description="Bayesian shrinkage weight w_i")


class PlayerBowlingProfile(BaseModel):
    player_id: int = Field(..., description="Unique player identifier")
    player_name: str = Field(..., description="Full player name")
    teams: List[str] = Field(default_factory=list, description="Teams")
    competitions: List[str] = Field(default_factory=list, description="Competitions")
    clutch_iq: float = Field(..., description="Bayesian Clutch IQ score [0, 100]")
    rank: Optional[int] = Field(None, description="Primary cohort rank (1 to 219)")
    cohort: str = Field(..., description="'primary' (>= 50 legal balls) or 'emerging' (< 50)")
    assignment_status: str = Field(..., description="'fitted' or 'provisional'")
    archetype_name: str = Field(..., description="Phase 4 empirical cricket archetype")
    player_archetype_explanation: str = Field(..., description="Player-level archetype narrative")
    
    # Pressure Metrics
    legal_balls: int = Field(..., description="Pressure legal balls bowled")
    runs_conceded: int = Field(..., description="Pressure bowler runs conceded")
    bowler_wickets: int = Field(..., description="Pressure bowler-creditable wickets")
    economy_rate: float = Field(..., description="Pressure economy rate (RPO)")
    bowling_strike_rate: Optional[float] = Field(None, description="Pressure balls per wicket (null if 0 wickets)")
    bowling_average: Optional[float] = Field(None, description="Pressure runs per wicket (null if 0 wickets)")
    wickets_per_legal_ball: float = Field(..., description="Wicket potency rate per delivery")
    dot_ball_pct: float = Field(..., description="Pressure dot-ball %")
    boundary_balls_conceded_per_100_legal_balls: float = Field(..., description="Boundaries conceded per 100 balls")
    fours_conceded: int = Field(..., description="Pressure fours conceded")
    sixes_conceded: int = Field(..., description="Pressure sixes conceded")
    match_count: int = Field(..., description="Distinct pressure matches")
    
    # Baseline Metrics
    balls_baseline: Optional[int] = Field(None, description="Baseline legal balls bowled")
    runs_conceded_baseline: Optional[int] = Field(None, description="Baseline runs conceded")
    wickets_baseline: Optional[int] = Field(None, description="Baseline wickets taken")
    econ_baseline: Optional[float] = Field(None, description="Baseline economy rate")
    wkt_sr_baseline: Optional[float] = Field(None, description="Baseline bowling strike rate")
    dot_pct_baseline: Optional[float] = Field(None, description="Baseline dot-ball %")
    boundary_balls_per_100_baseline: Optional[float] = Field(None, description="Baseline boundaries conceded per 100 balls")
    
    # Regularized & Shrunk Deltas
    reg_econ_base: float = Field(..., description="Regularized baseline economy rate")
    raw_delta_economy: float = Field(..., description="Raw delta economy over regularized baseline")
    shrunk_delta_economy: float = Field(..., description="Bayesian credibility-shrunk delta economy")
    reliability_weight: float = Field(..., description="Bayesian shrinkage weight w_i")


class PlayerComparisonItem(BaseModel):
    player_id: int = Field(..., description="Unique player identifier")
    player_name: str = Field(..., description="Full player name")
    teams: List[str] = Field(default_factory=list, description="Teams")
    batting: Optional[PlayerBattingProfile] = Field(None, description="Batting profile if available")
    bowling: Optional[PlayerBowlingProfile] = Field(None, description="Bowling profile if available")


class PlayerComparisonResponse(BaseModel):
    players: List[PlayerComparisonItem] = Field(..., description="List of compared player profiles")
    compared_count: int = Field(..., description="Number of players compared")

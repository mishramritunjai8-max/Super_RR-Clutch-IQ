"""
SUPER RR — CLUTCH IQ
Analytics & Pressure Summary Pydantic Schemas
"""

from typing import List
from pydantic import BaseModel, Field


class AnalyticsSummaryResponse(BaseModel):
    total_matches: int = Field(..., description="Total matches in dataset")
    completed_matches: int = Field(..., description="Completed matches with result")
    abandoned_matches: int = Field(..., description="Abandoned or no-result matches")
    total_deliveries: int = Field(..., description="Total deliveries across all innings (200,999)")
    regular_innings_deliveries: int = Field(..., description="Deliveries in regular innings 1-2 (200,961)")
    super_over_deliveries: int = Field(..., description="Deliveries in Super Overs innings >= 3 (38)")
    total_team_runs: int = Field(..., description="Total team runs scored across regular innings (281,418)")
    total_batter_runs: int = Field(..., description="Total runs scored off the bat (269,506)")
    total_extras_runs: int = Field(..., description="Total extras conceded (11,912)")
    total_bowler_wickets: int = Field(..., description="Total bowler-creditable wickets (10,261)")
    total_batters_count: int = Field(..., description="Total batters in regular innings (888)")
    total_bowlers_count: int = Field(..., description="Total bowlers in regular innings (647)")
    pressure_deliveries_count: int = Field(..., description="Deliveries under approved any-pressure union (53,453)")
    baseline_deliveries_count: int = Field(..., description="Deliveries under clean baseline (147,508)")
    pressure_percentage: float = Field(..., description="Percentage of regular deliveries occurring under pressure")
    seasons_covered: List[str] = Field(..., description="List of tournament seasons covered")
    competitions_count: int = Field(..., description="Count of distinct series / competitions represented")


class PressureSegmentSummary(BaseModel):
    segment_name: str = Field(..., description="Pressure category name")
    total_deliveries: int = Field(..., description="Total deliveries bowled in this segment")
    legal_balls: int = Field(..., description="Total legal balls bowled")
    balls_faced: int = Field(..., description="Total balls faced by batters (excluding wides)")
    total_matches: int = Field(..., description="Matches containing deliveries in this segment")
    unique_batters: int = Field(..., description="Unique batters participating")
    unique_bowlers: int = Field(..., description="Unique bowlers participating")
    total_runs_off_bat: int = Field(..., description="Runs scored off the bat")
    bowler_runs_conceded: int = Field(..., description="Runs charged to bowlers")
    team_innings_runs: int = Field(..., description="Total runs scored by teams including extras")
    bowler_wickets: int = Field(..., description="Bowler-creditable wickets")
    total_dismissals: int = Field(..., description="Total dismissals including run outs")
    fours: int = Field(..., description="Fours scored")
    sixes: int = Field(..., description="Sixes scored")
    dot_balls: int = Field(..., description="Dot balls bowled")
    batting_strike_rate: float = Field(..., description="Aggregate batting strike rate")
    bowling_economy: float = Field(..., description="Aggregate bowling economy rate (RPO)")
    bowling_strike_rate: float = Field(..., description="Aggregate bowling strike rate (balls/wkt)")
    bowling_average: float = Field(..., description="Aggregate bowling average (runs/wkt)")
    boundary_balls_conceded_per_100_legal_balls: float = Field(..., description="Boundaries conceded per 100 legal balls")
    boundary_runs_conceded_pct: float = Field(..., description="Percentage of runs scored in boundaries")
    overall_dot_percentage: float = Field(..., description="Percentage of deliveries resulting in zero runs")


class PressureAnalyticsResponse(BaseModel):
    segments: List[PressureSegmentSummary] = Field(..., description="Summary statistics for all 8 cricket segments")
    note: str = Field(..., description="Methodological note regarding set algebra and Super Over quarantine")

"""
SUPER RR — CLUTCH IQ
Phase 2: Baseline Comparison & Performance Delta Engine

Compares player performance in pressure situations against their clean,
unpolluted regular baseline (non-pressure league play in overs 1-15).
Ensures zero baseline contamination and transparent delta calculations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import numpy as np
from backend.analytics.batting_metrics import calculate_batting_metrics
from backend.analytics.bowling_metrics import calculate_bowling_metrics


def build_batting_pressure_comparison(
    pressure_df: pd.DataFrame,
    baseline_df: pd.DataFrame,
    segment_name: str,
    players_master_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Computes batting metrics under a pressure segment and joins with non-pressure baseline.
    Calculates elevation deltas: Delta Strike Rate, Delta Dot %, Delta Boundary %.
    """
    p_metrics = calculate_batting_metrics(pressure_df, segment_name=segment_name, players_master_df=players_master_df)
    b_metrics = calculate_batting_metrics(baseline_df, segment_name="baseline", players_master_df=players_master_df)

    if len(p_metrics) == 0:
        return pd.DataFrame()

    # Rename baseline columns for clean merging
    b_subset = b_metrics[[
        'player_id', 'total_runs', 'balls_faced', 'batting_average', 'strike_rate',
        'dot_ball_pct', 'boundary_run_pct', 'boundary_ball_pct', 'match_count', 'innings_count'
    ]].rename(columns={
        'total_runs': 'runs_baseline',
        'balls_faced': 'balls_baseline',
        'batting_average': 'avg_baseline',
        'strike_rate': 'sr_baseline',
        'dot_ball_pct': 'dot_pct_baseline',
        'boundary_run_pct': 'boundary_run_pct_baseline',
        'boundary_ball_pct': 'boundary_ball_pct_baseline',
        'match_count': 'matches_baseline',
        'innings_count': 'innings_baseline'
    })

    merged = pd.merge(p_metrics, b_subset, on='player_id', how='left')

    # Fill default values for players with no baseline data (e.g. death-only pinch hitters)
    merged['sr_baseline'] = merged['sr_baseline'].fillna(0.0)
    merged['dot_pct_baseline'] = merged['dot_pct_baseline'].fillna(0.0)
    merged['boundary_run_pct_baseline'] = merged['boundary_run_pct_baseline'].fillna(0.0)

    # Compute Elevation Deltas
    # Delta SR = SR_pressure - SR_baseline (higher is better)
    merged['delta_strike_rate'] = np.where(
        merged['balls_baseline'] > 0,
        np.round(merged['strike_rate'] - merged['sr_baseline'], 2),
        np.nan
    )

    # Delta Dot % = Dot%_baseline - Dot%_pressure (positive means fewer dots under pressure)
    merged['delta_dot_pct'] = np.where(
        merged['balls_baseline'] > 0,
        np.round(merged['dot_pct_baseline'] - merged['dot_ball_pct'], 2),
        np.nan
    )

    # Delta Boundary % = Boundary%_pressure - Boundary%_baseline (higher is better)
    merged['delta_boundary_run_pct'] = np.where(
        merged['balls_baseline'] > 0,
        np.round(merged['boundary_run_pct'] - merged['boundary_run_pct_baseline'], 2),
        np.nan
    )

    # Delta Batting Average
    merged['delta_batting_avg'] = np.where(
        (merged['batting_average'].notnull()) & (merged['avg_baseline'].notnull()),
        np.round(merged['batting_average'] - merged['avg_baseline'], 2),
        np.nan
    )

    return merged


def build_bowling_pressure_comparison(
    pressure_df: pd.DataFrame,
    baseline_df: pd.DataFrame,
    segment_name: str,
    players_master_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Computes bowling metrics under a pressure segment and joins with non-pressure baseline.
    Calculates elevation deltas: Delta Economy, Delta Dot %, Delta Wicket Strike Rate.
    """
    p_metrics = calculate_bowling_metrics(pressure_df, segment_name=segment_name, players_master_df=players_master_df)
    b_metrics = calculate_bowling_metrics(baseline_df, segment_name="baseline", players_master_df=players_master_df)

    if len(p_metrics) == 0:
        return pd.DataFrame()

    # Rename baseline columns
    b_subset = b_metrics[[
        'player_id', 'legal_balls', 'runs_conceded', 'bowler_wickets',
        'economy_rate', 'bowling_average', 'bowling_strike_rate',
        'dot_ball_pct', 'boundary_balls_conceded_per_100_legal_balls',
        'boundary_runs_conceded_pct', 'boundary_conceded_pct',
        'match_count', 'innings_count'
    ]].rename(columns={
        'legal_balls': 'balls_baseline',
        'runs_conceded': 'runs_conceded_baseline',
        'bowler_wickets': 'wickets_baseline',
        'economy_rate': 'econ_baseline',
        'bowling_average': 'avg_baseline',
        'bowling_strike_rate': 'wkt_sr_baseline',
        'dot_ball_pct': 'dot_pct_baseline',
        'boundary_balls_conceded_per_100_legal_balls': 'boundary_balls_per_100_baseline',
        'boundary_runs_conceded_pct': 'boundary_runs_pct_baseline',
        'boundary_conceded_pct': 'boundary_pct_baseline',
        'match_count': 'matches_baseline',
        'innings_count': 'innings_baseline'
    })

    merged = pd.merge(p_metrics, b_subset, on='player_id', how='left')

    # Compute Elevation Deltas
    # Delta Economy = Econ_baseline - Econ_pressure (positive means lower economy under pressure)
    merged['delta_economy'] = np.where(
        merged['econ_baseline'].notnull(),
        np.round(merged['econ_baseline'] - merged['economy_rate'], 2),
        np.nan
    )

    # Delta Dot % = Dot%_pressure - Dot%_baseline (positive means more dots created under pressure)
    merged['delta_dot_pct'] = np.where(
        merged['dot_pct_baseline'].notnull(),
        np.round(merged['dot_ball_pct'] - merged['dot_pct_baseline'], 2),
        np.nan
    )

    # Delta Boundary Balls Conceded per 100 Legal Balls (positive means fewer boundaries conceded per 100 balls)
    merged['delta_boundary_balls_per_100'] = np.where(
        merged['boundary_balls_per_100_baseline'].notnull(),
        np.round(merged['boundary_balls_per_100_baseline'] - merged['boundary_balls_conceded_per_100_legal_balls'], 2),
        np.nan
    )
    merged['delta_boundary_conceded_pct'] = merged['delta_boundary_balls_per_100']

    # Delta Boundary Runs Conceded % = % of runs from boundaries (positive means smaller % of runs from boundaries under pressure)
    merged['delta_boundary_runs_pct'] = np.where(
        merged['boundary_runs_pct_baseline'].notnull(),
        np.round(merged['boundary_runs_pct_baseline'] - merged['boundary_runs_conceded_pct'], 2),
        np.nan
    )

    # Delta Wicket Strike Rate = WktSR_baseline - WktSR_pressure (positive means wickets taken in fewer balls)
    merged['delta_wicket_sr'] = np.where(
        (merged['bowling_strike_rate'].notnull()) & (merged['wkt_sr_baseline'].notnull()),
        np.round(merged['wkt_sr_baseline'] - merged['bowling_strike_rate'], 2),
        np.nan
    )

    return merged

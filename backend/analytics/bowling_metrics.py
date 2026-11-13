"""
SUPER RR — CLUTCH IQ
Phase 2: Bowling Metrics Calculation Engine

Calculates comprehensive player-level bowling metrics for any delivery slice.
Groups strictly by player_id, preserving all players and handling edge cases.
"""

import pandas as pd
import numpy as np


def calculate_bowling_metrics(
    deliveries_df: pd.DataFrame,
    segment_name: str = "overall",
    players_master_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Computes bowling metrics for all bowlers who bowled in the given deliveries slice.
    
    Rules:
    - Legal balls exclude wides and no-balls (Overstep and other).
    - Runs conceded uses verified bowler_runs_conceded (excludes byes, leg-byes, penalty, extras_2_runs).
    - Bowler-credited wickets strictly includes: Bowled, Caught, LBW, Stump, Hit Wicket.
    - Economy rate = runs_conceded / (legal_balls / 6.0).
    - Bowling strike rate = legal_balls / bowler_wickets.
    - Bowling average = runs_conceded / bowler_wickets.
    - Dot balls = legal deliveries where bowler_runs_conceded == 0.
    """
    if len(deliveries_df) == 0:
        return pd.DataFrame()

    deliveries_df = deliveries_df.copy()
    deliveries_df['match_inn_id'] = deliveries_df['match_id'].astype(str) + '_' + deliveries_df['innings'].astype(str)

    # Legal deliveries only for dot ball calculation
    legal_mask = deliveries_df['is_legal_ball'] == True

    bowler_agg = deliveries_df.groupby('bowler_id').agg(
        total_deliveries=('is_legal_ball', 'count'),
        legal_balls=('is_legal_ball', 'sum'),
        runs_conceded=('bowler_runs_conceded', 'sum'),
        bowler_wickets=('is_bowler_wicket', 'sum'),
        fours_conceded=('is_four', 'sum'),
        sixes_conceded=('is_six', 'sum'),
        wides_conceded=('is_wide', 'sum'),
        noballs_conceded=('is_noball', 'sum'),
        match_count=('match_id', 'nunique'),
        innings_count=('match_inn_id', 'nunique')
    ).reset_index().rename(columns={'bowler_id': 'player_id'})

    # Calculate dot balls: legal delivery with bowler_runs_conceded == 0
    legal_dots = deliveries_df[legal_mask & (deliveries_df['bowler_runs_conceded'] == 0)]
    dots_map = legal_dots.groupby('bowler_id').size().to_dict()
    bowler_agg['dot_balls'] = bowler_agg['player_id'].map(dots_map).fillna(0).astype(int)

    # Derived Rate Metrics
    bowler_agg['overs_bowled'] = np.round(bowler_agg['legal_balls'] / 6.0, 2)
    
    # Economy Rate
    bowler_agg['economy_rate'] = np.where(
        bowler_agg['legal_balls'] > 0,
        np.round(bowler_agg['runs_conceded'] / (bowler_agg['legal_balls'] / 6.0), 2),
        np.nan
    )

    # Bowling Average (runs / wicket)
    bowler_agg['bowling_average'] = np.where(
        bowler_agg['bowler_wickets'] > 0,
        np.round(bowler_agg['runs_conceded'] / bowler_agg['bowler_wickets'], 2),
        np.nan
    )

    # Bowling Strike Rate (balls / wicket)
    bowler_agg['bowling_strike_rate'] = np.where(
        bowler_agg['bowler_wickets'] > 0,
        np.round(bowler_agg['legal_balls'] / bowler_agg['bowler_wickets'], 2),
        np.nan
    )

    # Dot Ball Percentage
    bowler_agg['dot_ball_pct'] = np.where(
        bowler_agg['legal_balls'] > 0,
        np.round((bowler_agg['dot_balls'] / bowler_agg['legal_balls']) * 100.0, 2),
        0.0
    )

    # Boundary Conceded Metrics
    # 1. Boundary balls conceded per 100 legal balls (boundary ball frequency)
    bowler_agg['boundary_balls_conceded_per_100_legal_balls'] = np.where(
        bowler_agg['legal_balls'] > 0,
        np.round(((bowler_agg['fours_conceded'] + bowler_agg['sixes_conceded']) / bowler_agg['legal_balls']) * 100.0, 2),
        0.0
    )
    # Retain alias for backward compatibility
    bowler_agg['boundary_conceded_pct'] = bowler_agg['boundary_balls_conceded_per_100_legal_balls']

    # 2. Boundary runs conceded percentage = (fours*4 + sixes*6) / runs_conceded * 100
    boundary_runs = (bowler_agg['fours_conceded'] * 4) + (bowler_agg['sixes_conceded'] * 6)
    bowler_agg['boundary_runs_conceded_pct'] = np.where(
        bowler_agg['runs_conceded'] > 0,
        np.round((boundary_runs / bowler_agg['runs_conceded']) * 100.0, 2),
        0.0
    )

    # Sample size indicator flags
    bowler_agg['has_min_sample_30'] = bowler_agg['legal_balls'] >= 30
    bowler_agg['has_min_sample_50'] = bowler_agg['legal_balls'] >= 50

    # Add player name from master players table
    bowler_agg['segment'] = segment_name
    if players_master_df is not None:
        bowler_agg = pd.merge(
            bowler_agg,
            players_master_df[['player_id', 'player_name']],
            on='player_id',
            how='left'
        )
    else:
        name_map = deliveries_df.groupby('bowler_id')['bowler_name'].first().to_dict()
        bowler_agg['player_name'] = bowler_agg['player_id'].map(name_map).fillna("Unknown Player")

    # Column ordering
    cols = [
        'player_id', 'player_name', 'segment', 'legal_balls', 'overs_bowled',
        'runs_conceded', 'bowler_wickets', 'economy_rate', 'bowling_average',
        'bowling_strike_rate', 'dot_balls', 'dot_ball_pct',
        'fours_conceded', 'sixes_conceded',
        'boundary_balls_conceded_per_100_legal_balls', 'boundary_runs_conceded_pct',
        'boundary_conceded_pct',
        'wides_conceded', 'noballs_conceded', 'innings_count', 'match_count',
        'has_min_sample_30', 'has_min_sample_50'
    ]
    return bowler_agg[cols].sort_values(['bowler_wickets', 'economy_rate'], ascending=[False, True]).reset_index(drop=True)

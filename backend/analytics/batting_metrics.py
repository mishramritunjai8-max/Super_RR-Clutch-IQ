"""
SUPER RR — CLUTCH IQ
Phase 2: Batting Metrics Calculation Engine

Calculates comprehensive player-level batting metrics for any delivery slice.
Groups strictly by player_id, preserving all players and handling edge cases.
"""

import pandas as pd
import numpy as np


def calculate_batting_metrics(
    deliveries_df: pd.DataFrame,
    segment_name: str = "overall",
    players_master_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Computes batting metrics for all batters who participated in the given deliveries slice.
    
    Rules:
    - Balls faced excludes wides, includes no-balls faced.
    - Dismissals attributed using dismissed_player_id (captures striker and non-striker dismissals).
    - Batting average = total_runs / dismissals (NaN if dismissals == 0).
    - Not-outs = max(0, innings_count - dismissals).
    - Handles zero denominators safely without throwing warnings.
    """
    if len(deliveries_df) == 0:
        return pd.DataFrame()

    # 1. Balls faced definition: exclude wides, include all legal deliveries and no-balls
    # extras_type != 'wide' (or is_wide == False)
    is_ball_faced = deliveries_df['extras_type'] != 'wide'
    balls_faced_df = deliveries_df[is_ball_faced].copy()

    # Precompute boolean columns for fast vectorized aggregation
    balls_faced_df['is_single'] = balls_faced_df['runs'] == 1
    balls_faced_df['is_double'] = balls_faced_df['runs'] == 2
    balls_faced_df['is_triple'] = balls_faced_df['runs'] == 3
    balls_faced_df['match_inn_id'] = balls_faced_df['match_id'].astype(str) + '_' + balls_faced_df['innings'].astype(str)

    # 2. Aggregations on deliveries faced as striker
    if len(balls_faced_df) > 0:
        bat_agg = balls_faced_df.groupby('striker_id').agg(
            total_runs=('runs', 'sum'),
            balls_faced=('runs', 'count'),
            fours=('is_four', 'sum'),
            sixes=('is_six', 'sum'),
            dot_balls=('is_dot_ball', 'sum'),
            singles=('is_single', 'sum'),
            doubles=('is_double', 'sum'),
            triples=('is_triple', 'sum'),
            match_count=('match_id', 'nunique'),
            innings_count=('match_inn_id', 'nunique')
        ).reset_index().rename(columns={'striker_id': 'player_id'})
    else:
        bat_agg = pd.DataFrame(columns=[
            'player_id', 'total_runs', 'balls_faced', 'fours', 'sixes',
            'dot_balls', 'singles', 'doubles', 'triples', 'match_count', 'innings_count'
        ])

    # 3. Dismissals aggregation using dismissed_player_id
    # Captures striker dismissals, non-striker run-outs, and retired outs
    wkts_df = deliveries_df[deliveries_df['is_wicket'] == True]
    if len(wkts_df) > 0:
        dismissals_agg = wkts_df.groupby('dismissed_player_id').size().reset_index().rename(
            columns={'dismissed_player_id': 'player_id', 0: 'dismissals'}
        )
        # Convert player_id to int
        dismissals_agg['player_id'] = dismissals_agg['player_id'].astype(int)
    else:
        dismissals_agg = pd.DataFrame(columns=['player_id', 'dismissals'])

    # 4. Merge batting stats with dismissals (outer join to capture diamond ducks with 0 balls faced)
    merged = pd.merge(bat_agg, dismissals_agg, on='player_id', how='outer')

    # Fill NaNs for numerical stats
    for col in ['total_runs', 'balls_faced', 'fours', 'sixes', 'dot_balls', 'singles', 'doubles', 'triples', 'match_count', 'innings_count', 'dismissals']:
        merged[col] = merged[col].fillna(0).astype(int)

    # If a player was only dismissed with 0 balls faced (diamond duck), innings_count and match_count are at least 1
    diamond_ducks = (merged['balls_faced'] == 0) & (merged['dismissals'] > 0)
    merged.loc[diamond_ducks, 'innings_count'] = np.maximum(1, merged.loc[diamond_ducks, 'innings_count'])
    merged.loc[diamond_ducks, 'match_count'] = np.maximum(1, merged.loc[diamond_ducks, 'match_count'])

    # 5. Derived Rate Metrics
    # Boundary runs and percentages
    merged['boundary_runs'] = (merged['fours'] * 4) + (merged['sixes'] * 6)
    merged['boundary_run_pct'] = np.where(
        merged['total_runs'] > 0,
        np.round((merged['boundary_runs'] / merged['total_runs']) * 100.0, 2),
        0.0
    )
    merged['boundary_ball_pct'] = np.where(
        merged['balls_faced'] > 0,
        np.round(((merged['fours'] + merged['sixes']) / merged['balls_faced']) * 100.0, 2),
        0.0
    )

    # Strike rate
    merged['strike_rate'] = np.where(
        merged['balls_faced'] > 0,
        np.round((merged['total_runs'] / merged['balls_faced']) * 100.0, 2),
        0.0
    )

    # Dot ball percentage
    merged['dot_ball_pct'] = np.where(
        merged['balls_faced'] > 0,
        np.round((merged['dot_balls'] / merged['balls_faced']) * 100.0, 2),
        0.0
    )

    # Not-outs & Averages
    merged['not_outs'] = np.maximum(0, merged['innings_count'] - merged['dismissals'])
    
    # Batting average: total_runs / dismissals (NaN if dismissals == 0)
    merged['batting_average'] = np.where(
        merged['dismissals'] > 0,
        np.round(merged['total_runs'] / merged['dismissals'], 2),
        np.nan
    )
    merged['runs_per_dismissal'] = merged['batting_average']

    # 6. Sample size indicator flags
    merged['has_min_sample_30'] = merged['balls_faced'] >= 30
    merged['has_min_sample_50'] = merged['balls_faced'] >= 50

    # 7. Add player name from master players table if available
    merged['segment'] = segment_name
    if players_master_df is not None:
        merged = pd.merge(
            merged,
            players_master_df[['player_id', 'player_name']],
            on='player_id',
            how='left'
        )
    else:
        # Fallback striker name from deliveries
        name_map = deliveries_df.groupby('striker_id')['striker_name'].first().to_dict()
        merged['player_name'] = merged['player_id'].map(name_map).fillna("Unknown Player")

    # Column ordering
    cols = [
        'player_id', 'player_name', 'segment', 'total_runs', 'balls_faced',
        'dismissals', 'not_outs', 'innings_count', 'match_count',
        'batting_average', 'strike_rate', 'runs_per_dismissal',
        'fours', 'sixes', 'boundary_runs', 'boundary_run_pct', 'boundary_ball_pct',
        'dot_balls', 'dot_ball_pct', 'singles', 'doubles', 'triples',
        'has_min_sample_30', 'has_min_sample_50'
    ]
    return merged[cols].sort_values(['total_runs', 'strike_rate'], ascending=[False, False]).reset_index(drop=True)

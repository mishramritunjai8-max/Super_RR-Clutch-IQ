"""
SUPER RR — CLUTCH IQ
Phase 2: Pressure Segmentation Module

Defines deterministic, delivery-level pressure filters and segment slices.
Guarantees zero outcome leakage and explicit baseline segregation.
"""

import pandas as pd
import numpy as np


def get_overall_regular_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """All deliveries in regular innings 1 and 2 (excludes Super Overs)."""
    return df[df['innings'] <= 2].copy()


def get_death_primary_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """Primary Death Overs: Overs 16 to 20 in regular innings."""
    return df[(df['overid'] >= 16) & (df['innings'] <= 2)].copy()


def get_death_stricter_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """Stricter Death Overs: Overs 17 to 20 in regular innings."""
    return df[(df['overid'] >= 17) & (df['innings'] <= 2)].copy()


def get_close_chase_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Situational Close Chase:
    Innings 2, <= 36 legal balls remaining, Required Run Rate >= 9.0, runs needed > 0.
    Evaluated immediately before each delivery without outcome leakage.
    """
    return df[(df['is_situational_close_chase'] == True) & (df['innings'] == 2)].copy()


def get_knockout_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """Knockout Matches: Eliminator, Qualifier, Semi Final, Final in regular innings."""
    return df[(df['is_knockout'] == True) & (df['innings'] <= 2)].copy()


def get_super_over_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """Super Overs: Innings 3 and 4 only. Dedicated tiebreak pressure."""
    return df[df['innings'] >= 3].copy()


def get_any_pressure_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combined Pressure: Union of Death Primary, Close Chase, and Knockouts.
    Avoids double-counting balls that satisfy multiple pressure definitions.
    """
    is_pressure = (
        (df['overid'] >= 16) |
        (df['is_situational_close_chase'] == True) |
        (df['is_knockout'] == True)
    )
    return df[is_pressure & (df['innings'] <= 2)].copy()


def get_non_pressure_baseline_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean Non-Pressure Baseline:
    Regular innings deliveries that have NO pressure tags:
    - Overs 1 to 15 (Powerplay and Middle overs)
    - NOT in close chase
    - NOT in knockout matches
    - NOT in super overs
    """
    is_non_pressure = (
        (df['innings'] <= 2) &
        (df['overid'] < 16) &
        (df['is_situational_close_chase'] == False) &
        (df['is_knockout'] == False)
    )
    return df[is_non_pressure].copy()


def compute_team_innings_runs(seg_df: pd.DataFrame) -> int:
    """Calculates total runs scored by the batting team on this slice (batter runs + extras)."""
    if len(seg_df) == 0:
        return 0
    team_runs = seg_df['runs'].copy()
    team_runs += seg_df['is_wide'].astype(int) * 1
    nb_mask = seg_df['is_noball']
    team_runs.loc[nb_mask] = 1 + seg_df.loc[nb_mask, 'runs'] + seg_df.loc[nb_mask, 'extras_2_runs']
    bye_mask = seg_df['is_bye'] | seg_df['is_legbye']
    team_runs.loc[bye_mask] = np.where(seg_df.loc[bye_mask, 'runs'] == 0, 1, seg_df.loc[bye_mask, 'runs'])
    pen_mask = seg_df['is_penalty']
    team_runs.loc[pen_mask] = 5
    return int(team_runs.sum())


def generate_pressure_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a consolidated summary table describing each segment's volume,
    cricket metrics, and distinct matches.
    Strictly verifies rate denominators:
    - Batting strike rate: batter runs / balls faced * 100 (excludes wides, includes no-balls)
    - Bowling economy: bowler runs conceded / (legal balls / 6)
    - Bowling strike rate: legal balls / bowler wickets
    - Bowling average: bowler runs conceded / bowler wickets
    - Innings scoring rate: total team runs / (legal balls / 6)
    - Boundary balls per 100 legal balls: (4s + 6s) / legal balls * 100
    - Boundary runs % conceded: (4s*4 + 6s*6) / bowler runs * 100
    """
    segments = {
        "Overall Regular (Innings 1-2)": get_overall_regular_deliveries(df),
        "Non-Pressure Baseline": get_non_pressure_baseline_deliveries(df),
        "Any Pressure (Union)": get_any_pressure_deliveries(df),
        "Death Primary (Overs 16-20)": get_death_primary_deliveries(df),
        "Death Stricter (Overs 17-20)": get_death_stricter_deliveries(df),
        "Close Chase (RRR >= 9, <= 36 balls)": get_close_chase_deliveries(df),
        "Knockout Matches": get_knockout_deliveries(df),
        "Super Overs (Innings >= 3)": get_super_over_deliveries(df)
    }

    summary_rows = []
    for name, seg_df in segments.items():
        total_deliveries = len(seg_df)
        legal_balls = int(seg_df['is_legal_ball'].sum()) if total_deliveries > 0 else 0
        balls_faced = int((seg_df['extras_type'] != 'wide').sum()) if total_deliveries > 0 else 0
        total_runs = int(seg_df['runs'].sum()) if total_deliveries > 0 else 0
        bowler_runs = int(seg_df['bowler_runs_conceded'].sum()) if total_deliveries > 0 else 0
        team_runs = compute_team_innings_runs(seg_df) if total_deliveries > 0 else 0
        bowler_wickets = int(seg_df['is_bowler_wicket'].sum()) if total_deliveries > 0 else 0
        total_wickets = int(seg_df['is_wicket'].sum()) if total_deliveries > 0 else 0
        dot_balls = int(seg_df['is_dot_ball'].sum()) if total_deliveries > 0 else 0
        fours = int(seg_df['is_four'].sum()) if total_deliveries > 0 else 0
        sixes = int(seg_df['is_six'].sum()) if total_deliveries > 0 else 0
        matches_count = seg_df['match_id'].nunique() if total_deliveries > 0 else 0
        strikers_count = seg_df['striker_id'].nunique() if total_deliveries > 0 else 0
        bowlers_count = seg_df['bowler_id'].nunique() if total_deliveries > 0 else 0

        # Exact audited rate metrics
        econ = round((bowler_runs / (legal_balls / 6.0)), 2) if legal_balls > 0 else 0.0
        bat_sr = round((total_runs / balls_faced) * 100, 2) if balls_faced > 0 else 0.0
        bowl_sr = round((legal_balls / bowler_wickets), 2) if bowler_wickets > 0 else None
        bowl_avg = round((bowler_runs / bowler_wickets), 2) if bowler_wickets > 0 else None
        innings_rpo = round((team_runs / (legal_balls / 6.0)), 2) if legal_balls > 0 else 0.0
        boundary_balls_per_100 = round(((fours + sixes) / legal_balls) * 100, 2) if legal_balls > 0 else 0.0
        boundary_runs_pct = round(((fours * 4 + sixes * 6) / bowler_runs) * 100, 2) if bowler_runs > 0 else 0.0
        dot_pct = round((dot_balls / legal_balls) * 100, 2) if legal_balls > 0 else 0.0

        summary_rows.append({
            "segment_name": name,
            "total_deliveries": total_deliveries,
            "legal_balls": legal_balls,
            "balls_faced": balls_faced,
            "total_matches": matches_count,
            "unique_batters": strikers_count,
            "unique_bowlers": bowlers_count,
            "total_runs_off_bat": total_runs,
            "bowler_runs_conceded": bowler_runs,
            "team_innings_runs": team_runs,
            "bowler_wickets": bowler_wickets,
            "total_dismissals": total_wickets,
            "fours": fours,
            "sixes": sixes,
            "dot_balls": dot_balls,
            "batting_strike_rate": bat_sr,
            "bowling_economy": econ,
            "bowling_strike_rate": bowl_sr,
            "bowling_average": bowl_avg,
            "innings_scoring_rate_rpo": innings_rpo,
            "boundary_balls_conceded_per_100_legal_balls": boundary_balls_per_100,
            "boundary_runs_conceded_pct": boundary_runs_pct,
            "overall_dot_percentage": dot_pct
        })

    return pd.DataFrame(summary_rows)

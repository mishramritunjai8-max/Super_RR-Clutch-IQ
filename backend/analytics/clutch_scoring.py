"""
SUPER RR — CLUTCH IQ
Phase 3: Clutch IQ Scoring & Bayesian Shrinkage Engine

Implements statistically defensible, explainable player-level Clutch IQ scoring
for batters and bowlers. Compares pressure performance against baseline with
Bayesian shrinkage regularizing uncertain estimates toward a neutral zero delta.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
from typing import Dict, Tuple, Optional


# =============================================================================
# 1. Empirical Population Baseline Priors (from Phase 2 non-pressure baseline)
# =============================================================================
POPULATION_PRIORS = {
    "batting": {
        "strike_rate": 133.67,
        "dot_ball_pct": 36.95,
        "boundary_ball_pct": 18.00,
        "batting_average": 30.13
    },
    "bowling": {
        "economy_rate": 8.28,
        "bowling_strike_rate": 21.84,
        "dot_ball_pct": 36.95,
        "boundary_balls_per_100": 18.00
    }
}

# Default Empirical-Bayes Shrinkage Parameters
DEFAULT_K_REL = 150.0  # Effective exposure threshold for 50% credibility weight
DEFAULT_K_BASE = 50.0  # Minimum sample for baseline credibility before shrinking to population prior

# Scoring Weights (set a priori based on T20 game theory)
BATTING_WEIGHTS = {
    "strike_rate": 0.40,
    "dot_ball_pct": 0.25,
    "boundary_ball_pct": 0.25,
    "batting_average": 0.10
}

BOWLING_WEIGHTS = {
    "economy_rate": 0.35,
    "bowling_strike_rate": 0.25,
    "dot_ball_pct": 0.20,
    "boundary_balls_conceded_per_100_legal_balls": 0.20
}


# =============================================================================
# 2. Bayesian Shrinkage Calculation
# =============================================================================
def calculate_credibility_weight(
    deliveries_count: pd.Series,
    matches_count: pd.Series,
    k_constant: float = DEFAULT_K_REL
) -> pd.Series:
    """
    Computes the Bayesian credibility weight w_i in [0, 1] for player i.
    Uses delivery volume N_i and match count M_i:
        E_i = N_i * sqrt(M_i)  (Effective match-weighted delivery exposure)
        w_i = E_i / (E_i + K)
    
    Properties:
    - w_i approaches 1.0 for large, multi-match samples.
    - w_i approaches 0.0 for small, single-match samples.
    - Shrinks estimates toward 0 (neutral) without reversing sign.
    """
    effective_exposure = deliveries_count * np.sqrt(np.maximum(1.0, matches_count))
    weight = effective_exposure / (effective_exposure + k_constant)
    return np.round(weight, 4)


def regularize_baseline(
    player_metric: pd.Series,
    baseline_balls: pd.Series,
    population_prior: float,
    k_base: float = DEFAULT_K_BASE
) -> pd.Series:
    """
    Regularizes a player's baseline metric toward the population baseline prior
    when the player's non-pressure sample size is small:
        Base_shrunk = (N_base / (N_base + K_base)) * Base_raw + (K_base / (N_base + K_base)) * Pop_prior
    
    Prevents tailenders or small-baseline batters/bowlers from receiving artificial
    extreme deltas due to a fluke baseline of 0 or near-0 runs/balls.
    """
    n_base = baseline_balls.fillna(0.0)
    raw_metric = player_metric.fillna(population_prior)
    weight = n_base / (n_base + k_base)
    reg_metric = weight * raw_metric + (1.0 - weight) * population_prior
    return np.round(reg_metric, 2)


# =============================================================================
# 3. Robust CDF Normalization
# =============================================================================
def robust_cdf_normalize(
    shrunk_deltas: pd.Series,
    scale_factor: float
) -> pd.Series:
    """
    Maps shrunk deltas into a 0-100 continuous score using the Gaussian CDF:
        Score = norm.cdf(shrunk_delta / (scale_factor * 1.5)) * 100.0
    
    Properties:
    - Exactly 50.0 when shrunk_delta == 0 (neutral expectation: player performs exactly as baseline).
    - > 50.0 when player elevates performance under pressure.
    - < 50.0 when player declines under pressure.
    - Naturally saturates towards 0 or 100 for transcendent/catastrophic performers without hard clipping.
    """
    if scale_factor <= 0 or np.isnan(scale_factor):
        return pd.Series(50.0, index=shrunk_deltas.index)
    
    z = shrunk_deltas / (scale_factor * 1.5)
    scores = norm.cdf(z) * 100.0
    return np.round(scores, 2)


# =============================================================================
# 4. Batting Clutch IQ Scoring Engine
# =============================================================================
def score_batting_clutch(
    bat_df: pd.DataFrame,
    k_rel: float = DEFAULT_K_REL,
    k_base: float = DEFAULT_K_BASE,
    weights: Dict[str, float] = BATTING_WEIGHTS
) -> pd.DataFrame:
    """
    Computes Batting Clutch IQ scores across all batters in the given pressure slice.
    Retains all raw metrics, baseline figures, deltas, shrunk deltas, normalized scores,
    and final composite Clutch IQ.
    """
    df = bat_df.copy()
    priors = POPULATION_PRIORS["batting"]

    # 1. Baseline Regularization (resolves missing or small baseline samples)
    df['n_base'] = df['balls_baseline'].fillna(0.0)
    df['reg_sr_base'] = regularize_baseline(df['sr_baseline'], df['n_base'], priors['strike_rate'], k_base)
    df['reg_dot_base'] = regularize_baseline(df['dot_pct_baseline'], df['n_base'], priors['dot_ball_pct'], k_base)
    df['reg_bound_base'] = regularize_baseline(df['boundary_ball_pct_baseline'], df['n_base'], priors['boundary_ball_pct'], k_base)
    df['reg_avg_base'] = regularize_baseline(df['avg_baseline'], df['n_base'], priors['batting_average'], k_base)

    # 2. Raw Delta Calculation (oriented so that positive is always improvement under pressure)
    # A. Strike Rate: higher under pressure is better
    df['raw_delta_strike_rate'] = np.round(df['strike_rate'] - df['reg_sr_base'], 2)

    # B. Dot Ball %: lower dot % under pressure is better (reduction in dots)
    df['raw_delta_dot_pct'] = np.round(df['reg_dot_base'] - df['dot_ball_pct'], 2)

    # C. Boundary Ball Frequency %: higher boundary frequency under pressure is better
    df['raw_delta_boundary_ball_pct'] = np.round(df['boundary_ball_pct'] - df['reg_bound_base'], 2)

    # D. Batting Average: higher average under pressure is better (NaN average imputed to total runs)
    press_avg = df['batting_average'].fillna(df['total_runs'].astype(float))
    df['raw_delta_batting_avg'] = np.round(press_avg - df['reg_avg_base'], 2)

    # 3. Bayesian Reliability Weight
    df['reliability_weight'] = calculate_credibility_weight(df['balls_faced'], df['match_count'], k_constant=k_rel)

    # 4. Bayesian Shrunk Deltas (never reverses direction; shrinks toward 0)
    df['shrunk_delta_strike_rate'] = np.round(df['raw_delta_strike_rate'] * df['reliability_weight'], 2)
    df['shrunk_delta_dot_pct'] = np.round(df['raw_delta_dot_pct'] * df['reliability_weight'], 2)
    df['shrunk_delta_boundary_ball_pct'] = np.round(df['raw_delta_boundary_ball_pct'] * df['reliability_weight'], 2)
    df['shrunk_delta_batting_avg'] = np.round(df['raw_delta_batting_avg'] * df['reliability_weight'], 2)

    # 5. Normalization Scale Factors (using std of shrunk deltas across qualified batters)
    qual = df[df['balls_faced'] >= 50]
    scale_sr = qual['shrunk_delta_strike_rate'].std() if len(qual) > 0 else df['shrunk_delta_strike_rate'].std()
    scale_dot = qual['shrunk_delta_dot_pct'].std() if len(qual) > 0 else df['shrunk_delta_dot_pct'].std()
    scale_bound = qual['shrunk_delta_boundary_ball_pct'].std() if len(qual) > 0 else df['shrunk_delta_boundary_ball_pct'].std()
    scale_avg = qual['shrunk_delta_batting_avg'].std() if len(qual) > 0 else df['shrunk_delta_batting_avg'].std()

    # 6. Normalized Metric Scores (0-100 scale, 50.0 is neutral)
    df['norm_score_strike_rate'] = robust_cdf_normalize(df['shrunk_delta_strike_rate'], scale_sr)
    df['norm_score_dot_pct'] = robust_cdf_normalize(df['shrunk_delta_dot_pct'], scale_dot)
    df['norm_score_boundary_ball_pct'] = robust_cdf_normalize(df['shrunk_delta_boundary_ball_pct'], scale_bound)
    df['norm_score_batting_avg'] = robust_cdf_normalize(df['shrunk_delta_batting_avg'], scale_avg)

    # 7. Final Batting Clutch IQ (0-100 weighted composite)
    w1, w2, w3, w4 = weights['strike_rate'], weights['dot_ball_pct'], weights['boundary_ball_pct'], weights['batting_average']
    df['clutch_iq'] = np.round(
        w1 * df['norm_score_strike_rate'] +
        w2 * df['norm_score_dot_pct'] +
        w3 * df['norm_score_boundary_ball_pct'] +
        w4 * df['norm_score_batting_avg'],
        2
    )

    # Sample eligibility flag
    df['is_primary_eligible'] = df['balls_faced'] >= 50

    return df


# =============================================================================
# 5. Bowling Clutch IQ Scoring Engine
# =============================================================================
def score_bowling_clutch(
    bowl_df: pd.DataFrame,
    k_rel: float = DEFAULT_K_REL,
    k_base: float = DEFAULT_K_BASE,
    weights: Dict[str, float] = BOWLING_WEIGHTS
) -> pd.DataFrame:
    """
    Computes Bowling Clutch IQ scores across all bowlers in the given pressure slice.
    Retains all raw metrics, baseline figures, deltas, shrunk deltas, normalized scores,
    and final composite Clutch IQ.
    """
    df = bowl_df.copy()
    priors = POPULATION_PRIORS["bowling"]

    # 1. Baseline Regularization
    df['n_base'] = df['balls_baseline'].fillna(0.0)
    df['reg_econ_base'] = regularize_baseline(df['econ_baseline'], df['n_base'], priors['economy_rate'], k_base)
    df['reg_wkt_sr_base'] = regularize_baseline(df['wkt_sr_baseline'], df['n_base'], priors['bowling_strike_rate'], k_base)
    df['reg_dot_base'] = regularize_baseline(df['dot_pct_baseline'], df['n_base'], priors['dot_ball_pct'], k_base)
    df['reg_bound_base'] = regularize_baseline(df['boundary_balls_per_100_baseline'], df['n_base'], priors['boundary_balls_per_100'], k_base)

    # 2. Raw Delta Calculation (oriented so that positive is always improvement under pressure)
    # A. Economy Rate Suppression: Econ_baseline - Econ_pressure (positive means lower economy)
    df['raw_delta_economy'] = np.round(df['reg_econ_base'] - df['economy_rate'], 2)

    # B. Wicket Strike Rate Elevation: WktSR_baseline - WktSR_pressure (positive means wickets taken in fewer balls)
    # For bowlers with 0 pressure wickets, WktSR is bounded at legal_balls delivered
    press_wkt_sr = np.where(df['bowler_wickets'] > 0, df['bowling_strike_rate'], np.maximum(50.0, df['legal_balls'].astype(float)))
    df['raw_delta_wicket_sr'] = np.round(df['reg_wkt_sr_base'] - press_wkt_sr, 2)

    # C. Dot Ball % Elevation: Dot%_pressure - Dot%_baseline (positive means more dots under pressure)
    df['raw_delta_dot_pct'] = np.round(df['dot_ball_pct'] - df['reg_dot_base'], 2)

    # D. Boundary Balls Conceded Suppression: BoundaryBalls%_baseline - BoundaryBalls%_pressure (positive means fewer boundaries)
    df['raw_delta_boundary_balls'] = np.round(df['reg_bound_base'] - df['boundary_balls_conceded_per_100_legal_balls'], 2)

    # 3. Bayesian Reliability Weight
    df['reliability_weight'] = calculate_credibility_weight(df['legal_balls'], df['match_count'], k_constant=k_rel)

    # 4. Bayesian Shrunk Deltas (never reverses direction; shrinks toward 0)
    df['shrunk_delta_economy'] = np.round(df['raw_delta_economy'] * df['reliability_weight'], 2)
    df['shrunk_delta_wicket_sr'] = np.round(df['raw_delta_wicket_sr'] * df['reliability_weight'], 2)
    df['shrunk_delta_dot_pct'] = np.round(df['raw_delta_dot_pct'] * df['reliability_weight'], 2)
    df['shrunk_delta_boundary_balls'] = np.round(df['raw_delta_boundary_balls'] * df['reliability_weight'], 2)

    # 5. Normalization Scale Factors (using std of shrunk deltas across qualified bowlers)
    qual = df[df['legal_balls'] >= 50]
    scale_econ = qual['shrunk_delta_economy'].std() if len(qual) > 0 else df['shrunk_delta_economy'].std()
    scale_wkt_sr = qual['shrunk_delta_wicket_sr'].std() if len(qual) > 0 else df['shrunk_delta_wicket_sr'].std()
    scale_dot = qual['shrunk_delta_dot_pct'].std() if len(qual) > 0 else df['shrunk_delta_dot_pct'].std()
    scale_bound = qual['shrunk_delta_boundary_balls'].std() if len(qual) > 0 else df['shrunk_delta_boundary_balls'].std()

    # 6. Normalized Metric Scores (0-100 scale, 50.0 is neutral)
    df['norm_score_economy'] = robust_cdf_normalize(df['shrunk_delta_economy'], scale_econ)
    df['norm_score_wicket_sr'] = robust_cdf_normalize(df['shrunk_delta_wicket_sr'], scale_wkt_sr)
    df['norm_score_dot_pct'] = robust_cdf_normalize(df['shrunk_delta_dot_pct'], scale_dot)
    df['norm_score_boundary_balls'] = robust_cdf_normalize(df['shrunk_delta_boundary_balls'], scale_bound)

    # 7. Final Bowling Clutch IQ (0-100 weighted composite)
    w1, w2, w3, w4 = weights['economy_rate'], weights['bowling_strike_rate'], weights['dot_ball_pct'], weights['boundary_balls_conceded_per_100_legal_balls']
    df['clutch_iq'] = np.round(
        w1 * df['norm_score_economy'] +
        w2 * df['norm_score_wicket_sr'] +
        w3 * df['norm_score_dot_pct'] +
        w4 * df['norm_score_boundary_balls'],
        2
    )

    # Sample eligibility flag
    df['is_primary_eligible'] = df['legal_balls'] >= 50

    return df

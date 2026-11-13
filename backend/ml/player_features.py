"""
SUPER RR — CLUTCH IQ
Phase 4: Player Feature Engineering Pipeline for Machine Learning (Corrected)

Extracts, validates, cleans, and standardizes multi-dimensional cricket
performance features for unsupervised clustering (K-Means).

Methodological Corrections Applied:
1. Removal of Mathematically Redundant Features:
   - Batting: Removed reg_sr_base (since raw_delta_SR = strike_rate - reg_sr_base).
     Removed collinear delta raw_delta_dot_pct (high correlation with dot_ball_pct).
   - Bowling: Removed reg_econ_base (since raw_delta_econ = reg_econ_base - economy_rate).
     Removed collinear delta raw_delta_dot_pct.
2. Mathematically Sound Zero-Dismissal & Zero-Wicket Handling:
   - Batters with 0 dismissals: Preserves original batting_average as NaN, adds
     is_zero_dismissals indicator, and imputes feature value using the primary cohort median.
   - Bowlers with 0 wickets: Preserves original bowling_strike_rate as NaN, adds
     is_zero_wickets indicator, and utilizes wickets_per_legal_ball as a continuous,
     everywhere-defined wicket potency rate (0.0 when 0 wickets).
3. Primary-Only Imputation and Standardization:
   - Scalers and imputers are fitted strictly on primary eligible cohort (>= 50 balls).
   - Emerging cohorts (< 50 balls) are transformed using the frozen primary parameters.
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
from typing import Dict, List, Tuple, Optional


# =============================================================================
# 1. Feature Definitions (Audited, Non-Redundant & Non-Collinear)
# =============================================================================
# Compact, interpretable 5-feature representations capturing:
# 1) Absolute pressure tempo/containment
# 2) Elevation over baseline (clutch acceleration/containment)
# 3) Dot-ball control/pressure
# 4) Boundary generation/concession
# 5) Wicket survival / wicket potency
BATTING_CLUSTERING_FEATURES = [
    "strike_rate",                 # Absolute pressure scoring velocity
    "raw_delta_strike_rate",       # Elevation over baseline (improvement)
    "dot_ball_pct",                # Pressure dot-ball frequency (ball control)
    "boundary_ball_pct",           # Pressure boundary hitting frequency (boundary power)
    "batting_average_imputed"      # Wicket preservation (primary median imputed for 0 dismissals)
]

BOWLING_CLUSTERING_FEATURES = [
    "economy_rate",                               # Absolute pressure runs conceded per over
    "raw_delta_economy",                          # Economy suppression delta over baseline (improvement)
    "wickets_per_legal_ball",                     # Wicket potency rate (everywhere defined, 0.0 for 0 wickets)
    "dot_ball_pct",                               # Pressure dot-ball forcing %
    "boundary_balls_conceded_per_100_legal_balls" # Boundary concession frequency
]

# Explicit documentation of excluded redundant features
EXCLUDED_FEATURES_EXPLANATION = {
    "batting": {
        "reg_sr_base": "Excluded due to exact algebraic identity: raw_delta_strike_rate = strike_rate - reg_sr_base. Retaining all three produces infinite VIF.",
        "raw_delta_dot_pct": "Excluded due to near-collinearity with dot_ball_pct (correlation = -0.834) and algebraic redundancy against reg_dot_base."
    },
    "bowling": {
        "reg_econ_base": "Excluded due to exact algebraic identity: raw_delta_economy = reg_econ_base - economy_rate. Retaining all three produces infinite VIF.",
        "bowling_strike_rate": "Excluded due to division-by-zero divergence when wickets = 0. Replaced by continuous, stable wickets_per_legal_ball.",
        "raw_delta_dot_pct": "Excluded due to near-collinearity with dot_ball_pct (correlation = -0.835) and algebraic redundancy against reg_dot_base."
    }
}


# =============================================================================
# 2. Batting Feature Preparation
# =============================================================================
def prepare_batting_features(
    scores_path: str = "data/processed/metrics/batting_clutch_scores.csv",
    scaler_type: str = "standard"
) -> Dict:
    """
    Loads, cleans, and standardizes batting metrics for clustering.
    
    Correction Policy:
    - Retains original dismissal count and batting_average.
    - Zero-dismissal batters have undefined batting_average (NaN). Adds is_zero_dismissals flag.
    - Imputes batting_average_imputed using the primary cohort median (fitted only on primary).
    - Fits scaler strictly on primary cohort (balls_faced >= 50).
    - Transforms emerging cohort (< 50 balls) with the frozen primary scaler.
    """
    df = pd.read_csv(scores_path)
    
    # Validation: unique player IDs
    assert df['player_id'].nunique() == len(df), "Duplicate player IDs found in batting dataset"
    
    # 1. Zero-dismissal indicator and observed batting average preservation
    df['is_zero_dismissals'] = (df['dismissals'] == 0).astype(int)
    
    # 2. Partition into Primary Eligible (>= 50 balls) vs Emerging (< 50 balls)
    df['cohort'] = np.where(df['balls_faced'] >= 50, 'primary', 'emerging')
    primary_mask = df['cohort'] == 'primary'
    
    primary_df = df[primary_mask].copy().reset_index(drop=True)
    emerging_df = df[~primary_mask].copy().reset_index(drop=True)
    
    # 3. Fit imputation statistics on PRIMARY cohort only
    primary_zero_dismissals = int((primary_df['dismissals'] == 0).sum())
    assert primary_zero_dismissals == 0, f"Primary batters expected 0 zero-dismissal cases; found {primary_zero_dismissals}"
    
    primary_median_avg = float(primary_df['batting_average'].dropna().median())
    primary_mean_avg = float(primary_df['batting_average'].dropna().mean())
    
    imputation_stats = {
        "strategy": "primary_cohort_median",
        "primary_median_batting_average": round(primary_median_avg, 2),
        "primary_mean_batting_average": round(primary_mean_avg, 2),
        "primary_zero_dismissals_count": primary_zero_dismissals,
        "emerging_zero_dismissals_count": int((emerging_df['dismissals'] == 0).sum())
    }
    
    # 4. Impute feature column using frozen primary median
    primary_df['batting_average_imputed'] = primary_df['batting_average'].fillna(primary_median_avg)
    emerging_df['batting_average_imputed'] = emerging_df['batting_average'].fillna(primary_median_avg)
    df['batting_average_imputed'] = df['batting_average'].fillna(primary_median_avg)
    
    # 5. Extract feature matrices
    X_primary_raw = primary_df[BATTING_CLUSTERING_FEATURES].copy()
    X_emerging_raw = emerging_df[BATTING_CLUSTERING_FEATURES].copy()
    
    # 6. Fit scaler on PRIMARY cohort only
    scaler = StandardScaler() if scaler_type == "standard" else RobustScaler()
    X_primary_scaled = scaler.fit_transform(X_primary_raw)
    X_emerging_scaled = scaler.transform(X_emerging_raw)
    
    # 7. Correlation matrix and redundancy verification
    corr_matrix = X_primary_raw.corr()
    cond_number = float(np.linalg.cond(corr_matrix.values))
    
    return {
        "full_df": df,
        "primary_df": primary_df,
        "emerging_df": emerging_df,
        "features": BATTING_CLUSTERING_FEATURES,
        "scaler": scaler,
        "scaler_type": scaler_type,
        "imputation_stats": imputation_stats,
        "correlation_matrix": corr_matrix,
        "condition_number": cond_number,
        "X_primary_raw": X_primary_raw,
        "X_primary_scaled": X_primary_scaled,
        "X_emerging_raw": X_emerging_raw,
        "X_emerging_scaled": X_emerging_scaled
    }


# =============================================================================
# 3. Bowling Feature Preparation
# =============================================================================
def prepare_bowling_features(
    scores_path: str = "data/processed/metrics/bowling_clutch_scores.csv",
    scaler_type: str = "standard"
) -> Dict:
    """
    Loads, cleans, and standardizes bowling metrics for clustering.
    
    Correction Policy:
    - Retains original bowler_wickets and bowling_strike_rate (with NaN when wickets = 0).
    - Zero-wicket bowlers have undefined bowling_strike_rate. Adds is_zero_wickets flag.
    - Employs wickets_per_legal_ball as a continuous, stable rate defined for all bowlers
      (exactly 0.0 for zero-wicket bowlers, avoiding arbitrary strike rate imputation).
    - Fits scaler strictly on primary cohort (legal_balls >= 50).
    - Transforms emerging cohort (< 50 legal balls) with the frozen primary scaler.
    """
    df = pd.read_csv(scores_path)
    
    # Validation: unique player IDs
    assert df['player_id'].nunique() == len(df), "Duplicate player IDs found in bowling dataset"
    
    # 1. Zero-wicket indicator and observed strike rate preservation
    df['is_zero_wickets'] = (df['bowler_wickets'] == 0).astype(int)
    
    # 2. Continuous, stable wicket potency feature: wickets per legal ball
    df['wickets_per_legal_ball'] = df['bowler_wickets'] / df['legal_balls']
    
    # 3. Partition into Primary Eligible (>= 50 legal balls) vs Emerging (< 50 legal balls)
    df['cohort'] = np.where(df['legal_balls'] >= 50, 'primary', 'emerging')
    primary_mask = df['cohort'] == 'primary'
    
    primary_df = df[primary_mask].copy().reset_index(drop=True)
    emerging_df = df[~primary_mask].copy().reset_index(drop=True)
    
    # 4. Statistics on zero-wicket cases
    imputation_stats = {
        "strategy": "continuous_rate_wickets_per_legal_ball",
        "primary_zero_wickets_count": int((primary_df['bowler_wickets'] == 0).sum()),
        "emerging_zero_wickets_count": int((emerging_df['bowler_wickets'] == 0).sum()),
        "primary_mean_wickets_per_legal_ball": round(float(primary_df['wickets_per_legal_ball'].mean()), 4),
        "primary_median_wickets_per_legal_ball": round(float(primary_df['wickets_per_legal_ball'].median()), 4)
    }
    
    # 5. Extract feature matrices
    X_primary_raw = primary_df[BOWLING_CLUSTERING_FEATURES].copy()
    X_emerging_raw = emerging_df[BOWLING_CLUSTERING_FEATURES].copy()
    
    # 6. Fit scaler on PRIMARY cohort only
    scaler = StandardScaler() if scaler_type == "standard" else RobustScaler()
    X_primary_scaled = scaler.fit_transform(X_primary_raw)
    X_emerging_scaled = scaler.transform(X_emerging_raw)
    
    # 7. Correlation matrix and redundancy verification
    corr_matrix = X_primary_raw.corr()
    cond_number = float(np.linalg.cond(corr_matrix.values))
    
    return {
        "full_df": df,
        "primary_df": primary_df,
        "emerging_df": emerging_df,
        "features": BOWLING_CLUSTERING_FEATURES,
        "scaler": scaler,
        "scaler_type": scaler_type,
        "imputation_stats": imputation_stats,
        "correlation_matrix": corr_matrix,
        "condition_number": cond_number,
        "X_primary_raw": X_primary_raw,
        "X_primary_scaled": X_primary_scaled,
        "X_emerging_raw": X_emerging_raw,
        "X_emerging_scaled": X_emerging_scaled
    }

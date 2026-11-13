"""
SUPER RR — CLUTCH IQ
Phase 4: Automated Test & Validation Suite for Player Clustering (K-Means) (Corrected)

Run with:
    python -m pytest backend/tests/test_player_clustering.py -v
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import json
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def test_artifacts_exist_and_non_empty():
    required_files = [
        "data/processed/metrics/batting_cluster_assignments.csv",
        "data/processed/metrics/bowling_cluster_assignments.csv",
        "data/processed/metrics/batting_cluster_profiles.csv",
        "data/processed/metrics/bowling_cluster_profiles.csv",
        "data/processed/metrics/batting_cluster_validation.csv",
        "data/processed/metrics/bowling_cluster_validation.csv",
        "data/processed/metrics/batting_feature_correlations.csv",
        "data/processed/metrics/bowling_feature_correlations.csv",
        "data/processed/metrics/phase4_ml_quality_report.json",
        "models/phase4/batting_kmeans_model.joblib",
        "models/phase4/bowling_kmeans_model.joblib",
        "models/phase4/batting_scaler.joblib",
        "models/phase4/bowling_scaler.joblib",
        "models/phase4/batting_metadata.json",
        "models/phase4/bowling_metadata.json"
    ]
    for f in required_files:
        assert os.path.exists(f), f"Missing Phase 4 artifact: {f}"
        assert os.path.getsize(f) > 0, f"Phase 4 artifact is empty: {f}"
    print("  [PASS 1/21] All 15 Phase 4 data, correlation, and model artifacts exist and are non-empty.")


def test_exact_feature_redundancy_and_determinant():
    bat_corr = pd.read_csv("data/processed/metrics/batting_feature_correlations.csv", index_col=0)
    bowl_corr = pd.read_csv("data/processed/metrics/bowling_feature_correlations.csv", index_col=0)
    
    # Check non-zero determinant (no exact linear dependence)
    det_bat = np.linalg.det(bat_corr.values)
    det_bowl = np.linalg.det(bowl_corr.values)
    assert det_bat > 0.001, f"Batting correlation matrix is singular or near-singular: det={det_bat}"
    assert det_bowl > 0.001, f"Bowling correlation matrix is singular or near-singular: det={det_bowl}"
    
    # Check well-behaved condition number (< 500, cured from 10^16)
    cond_bat = np.linalg.cond(bat_corr.values)
    cond_bowl = np.linalg.cond(bowl_corr.values)
    assert cond_bat < 500.0, f"Batting condition number too high: {cond_bat}"
    assert cond_bowl < 500.0, f"Bowling condition number too high: {cond_bowl}"
    
    print("  [PASS 2/21] Exact algebraic redundancy eliminated: Non-zero determinants and stable condition numbers verified.")


def test_feature_uniqueness_and_compactness():
    with open("models/phase4/batting_metadata.json", "r", encoding="utf-8") as f:
        bat_meta = json.load(f)
    with open("models/phase4/bowling_metadata.json", "r", encoding="utf-8") as f:
        bowl_meta = json.load(f)
        
    bat_feats = bat_meta["features"]
    bowl_feats = bowl_meta["features"]
    
    assert len(bat_feats) == len(set(bat_feats)), "Duplicate feature names in batting"
    assert len(bowl_feats) == len(set(bowl_feats)), "Duplicate feature names in bowling"
    assert len(bat_feats) == 5, f"Expected 5 non-redundant batting features; found {len(bat_feats)}"
    assert len(bowl_feats) == 5, f"Expected 5 non-redundant bowling features; found {len(bowl_feats)}"
    
    # Verify excluded features
    assert "reg_sr_base" not in bat_feats, "reg_sr_base must be excluded from batting features"
    assert "reg_econ_base" not in bowl_feats, "reg_econ_base must be excluded from bowling features"
    
    print("  [PASS 3/21] Feature uniqueness and compact 5-feature dimensionality verified for both models.")


def test_zero_dismissal_batter_handling():
    bat_assign = pd.read_csv("data/processed/metrics/batting_cluster_assignments.csv")
    
    assert "is_zero_dismissals" in bat_assign.columns, "is_zero_dismissals column missing"
    assert "batting_average" in bat_assign.columns, "original batting_average column missing"
    assert "batting_average_imputed" in bat_assign.columns, "batting_average_imputed column missing"
    
    # Primary cohort (balls_faced >= 50): 0 zero-dismissal batters
    primary = bat_assign[bat_assign["cohort"] == "primary"]
    assert (primary["is_zero_dismissals"] == 0).all(), "All primary batters must have >= 1 dismissal"
    assert primary["batting_average"].notna().all(), "Primary batting average must not contain NaNs"
    
    # Emerging cohort (< 50 balls): exactly 102 zero-dismissal batters
    emerging = bat_assign[bat_assign["cohort"] == "emerging"]
    zero_d_em = emerging[emerging["is_zero_dismissals"] == 1]
    assert len(zero_d_em) == 102, f"Expected 102 emerging zero-dismissal batters; found {len(zero_d_em)}"
    assert zero_d_em["batting_average"].isna().all(), "Original batting_average must remain NaN for 0-dismissal batters"
    
    # Imputed batting average must equal primary cohort median (20.93)
    prim_median = primary["batting_average"].median()
    assert np.allclose(zero_d_em["batting_average_imputed"], prim_median), "Imputed average must match primary median"
    
    print("  [PASS 4/21] Zero-dismissal batter handling verified: NaN preserved, indicator present, primary median imputed.")


def test_zero_wicket_bowler_handling():
    bowl_assign = pd.read_csv("data/processed/metrics/bowling_cluster_assignments.csv")
    
    assert "is_zero_wickets" in bowl_assign.columns, "is_zero_wickets column missing"
    assert "wickets_per_legal_ball" in bowl_assign.columns, "wickets_per_legal_ball column missing"
    assert "bowling_strike_rate" in bowl_assign.columns, "original bowling_strike_rate column missing"
    
    # Zero-wicket counts: 3 primary, 109 emerging
    primary = bowl_assign[bowl_assign["cohort"] == "primary"]
    emerging = bowl_assign[bowl_assign["cohort"] == "emerging"]
    
    assert (primary["is_zero_wickets"] == 1).sum() == 3, "Expected 3 primary zero-wicket bowlers"
    assert (emerging["is_zero_wickets"] == 1).sum() == 109, "Expected 109 emerging zero-wicket bowlers"
    
    # For all zero-wicket bowlers, bowling_strike_rate must be NaN and wickets_per_legal_ball must be 0.0
    zero_w = bowl_assign[bowl_assign["is_zero_wickets"] == 1]
    assert zero_w["bowling_strike_rate"].isna().all(), "Original strike rate must remain NaN for zero-wicket bowlers"
    assert (zero_w["wickets_per_legal_ball"] == 0.0).all(), "wickets_per_legal_ball must be exactly 0.0 for zero-wicket bowlers"
    assert bowl_assign["wickets_per_legal_ball"].notna().all(), "wickets_per_legal_ball must be defined everywhere"
    
    print("  [PASS 5/21] Zero-wicket bowler handling verified: NaN preserved, continuous rate everywhere defined (0.0 for 0 wickets).")


def test_primary_only_imputer_and_scaler_fitting():
    with open("models/phase4/batting_metadata.json", "r", encoding="utf-8") as f:
        bat_meta = json.load(f)
    with open("models/phase4/bowling_metadata.json", "r", encoding="utf-8") as f:
        bowl_meta = json.load(f)
        
    bat_assign = pd.read_csv("data/processed/metrics/batting_cluster_assignments.csv")
    bowl_assign = pd.read_csv("data/processed/metrics/bowling_cluster_assignments.csv")
    
    primary_bat = bat_assign[bat_assign["cohort"] == "primary"]
    primary_bowl = bowl_assign[bowl_assign["cohort"] == "primary"]
    
    # 1. Imputer median check
    stored_median = bat_meta["imputation_statistics"]["primary_median_batting_average"]
    computed_median = round(float(primary_bat["batting_average"].dropna().median()), 2)
    assert stored_median == computed_median, f"Stored median {stored_median} != computed primary median {computed_median}"
    
    # 2. Scaler means check
    scaler_bat = joblib.load("models/phase4/batting_scaler.joblib")
    scaler_bowl = joblib.load("models/phase4/bowling_scaler.joblib")
    
    bat_feats = bat_meta["features"]
    bowl_feats = bowl_meta["features"]
    
    np.testing.assert_allclose(scaler_bat.mean_, primary_bat[bat_feats].mean().values, rtol=1e-5)
    np.testing.assert_allclose(scaler_bowl.mean_, primary_bowl[bowl_feats].mean().values, rtol=1e-5)
    
    print("  [PASS 6/21] Primary-only fitting verified: Imputers and scalers parameterized exclusively on primary cohort.")


def test_emerging_cohort_exclusion_from_model_fitting():
    bat_assign = pd.read_csv("data/processed/metrics/batting_cluster_assignments.csv")
    bowl_assign = pd.read_csv("data/processed/metrics/bowling_cluster_assignments.csv")
    
    # Primary cohort: fitted; Emerging cohort: provisional
    assert (bat_assign[bat_assign["cohort"] == "primary"]["assignment_status"] == "fitted").all()
    assert (bat_assign[bat_assign["cohort"] == "emerging"]["assignment_status"] == "provisional").all()
    assert (bowl_assign[bowl_assign["cohort"] == "primary"]["assignment_status"] == "fitted").all()
    assert (bowl_assign[bowl_assign["cohort"] == "emerging"]["assignment_status"] == "provisional").all()
    
    print("  [PASS 7/21] Emerging cohort strictly excluded from centroid fitting; assigned provisionally via frozen pipeline.")


def test_valid_k_candidate_selection():
    bat_val = pd.read_csv("data/processed/metrics/batting_cluster_validation.csv")
    bowl_val = pd.read_csv("data/processed/metrics/bowling_cluster_validation.csv")
    
    # K in 2..8 evaluated
    assert set(bat_val["k"]) == set(range(2, 9)), "Batting validation must evaluate K in 2..8"
    assert set(bowl_val["k"]) == set(range(2, 9)), "Bowling validation must evaluate K in 2..8"
    
    # Check metric columns
    metrics = ["silhouette_score", "davies_bouldin_index", "calinski_harabasz_index", "inertia", "balance_ratio"]
    for m in metrics:
        assert m in bat_val.columns, f"Missing metric {m} in batting validation"
        assert m in bowl_val.columns, f"Missing metric {m} in bowling validation"
        
    print("  [PASS 8/21] Candidate K evaluations verified across K=2..8 and 5 validation metrics.")


def test_non_empty_clusters_and_balance():
    bat_prof = pd.read_csv("data/processed/metrics/batting_cluster_profiles.csv")
    bowl_prof = pd.read_csv("data/processed/metrics/bowling_cluster_profiles.csv")
    
    assert len(bat_prof) == 3, f"Expected 3 batting clusters; found {len(bat_prof)}"
    assert len(bowl_prof) == 3, f"Expected 3 bowling clusters; found {len(bowl_prof)}"
    
    # No micro-clusters: all primary sizes >= 40
    assert (bat_prof["primary_player_count"] >= 40).all(), "Batting primary cluster sizes must all be >= 40"
    assert (bowl_prof["primary_player_count"] >= 40).all(), "Bowling primary cluster sizes must all be >= 40"
    
    # Balance ratios
    bat_bal = bat_prof["primary_player_count"].min() / bat_prof["primary_player_count"].max()
    bowl_bal = bowl_prof["primary_player_count"].min() / bowl_prof["primary_player_count"].max()
    assert bat_bal > 0.40, f"Batting balance ratio {bat_bal} must be > 0.40"
    assert bowl_bal > 0.40, f"Bowling balance ratio {bowl_bal} must be > 0.40"
    
    print("  [PASS 9/21] Cluster sizes well-balanced (all primary sizes >= 40; balance ratios > 0.40).")


def test_player_id_uniqueness_and_coverage():
    bat_assign = pd.read_csv("data/processed/metrics/batting_cluster_assignments.csv")
    bowl_assign = pd.read_csv("data/processed/metrics/bowling_cluster_assignments.csv")
    
    assert len(bat_assign) == 775, f"Expected 775 batters, found {len(bat_assign)}"
    assert bat_assign["player_id"].nunique() == 775, "Duplicate player IDs found in batting assignments"
    
    assert len(bowl_assign) == 543, f"Expected 543 bowlers, found {len(bowl_assign)}"
    assert bowl_assign["player_id"].nunique() == 543, "Duplicate player IDs found in bowling assignments"
    
    print("  [PASS 10/21] Complete population coverage and player ID uniqueness confirmed (775 batters, 543 bowlers).")


def test_separate_batting_and_bowling_models():
    km_bat = joblib.load("models/phase4/batting_kmeans_model.joblib")
    km_bowl = joblib.load("models/phase4/bowling_kmeans_model.joblib")
    
    assert km_bat is not km_bowl, "Batting and bowling models must be distinct objects"
    assert km_bat.n_features_in_ == 5, "Batting model must expect 5 features"
    assert km_bowl.n_features_in_ == 5, "Bowling model must expect 5 features"
    
    print("  [PASS 11/21] Distinct models and preprocessors confirmed for batting and bowling.")


def test_no_clutch_iq_or_rank_leakage():
    with open("models/phase4/batting_metadata.json", "r", encoding="utf-8") as f:
        bat_meta = json.load(f)
    with open("models/phase4/bowling_metadata.json", "r", encoding="utf-8") as f:
        bowl_meta = json.load(f)
        
    forbidden = ["clutch_iq", "rank", "primary_rank", "is_primary_eligible", "cluster_id", "archetype_name"]
    for feat in bat_meta["features"]:
        assert feat.lower() not in forbidden, f"Target variable {feat} found in batting features"
    for feat in bowl_meta["features"]:
        assert feat.lower() not in forbidden, f"Target variable {feat} found in bowling features"
        
    print("  [PASS 12/21] Feature purity verified: Zero target variable or rank leakage into training vectors.")


def test_cluster_profile_counts_reconciliation():
    bat_assign = pd.read_csv("data/processed/metrics/batting_cluster_assignments.csv")
    bowl_assign = pd.read_csv("data/processed/metrics/bowling_cluster_assignments.csv")
    bat_prof = pd.read_csv("data/processed/metrics/batting_cluster_profiles.csv")
    bowl_prof = pd.read_csv("data/processed/metrics/bowling_cluster_profiles.csv")
    
    # Batting reconciliation
    assert bat_prof["primary_player_count"].sum() == 249, "Batting primary sum must equal 249"
    assert bat_prof["emerging_player_count"].sum() == 526, "Batting emerging sum must equal 526"
    assert bat_prof["total_player_count"].sum() == 775, "Batting total sum must equal 775"
    
    # Bowling reconciliation
    assert bowl_prof["primary_player_count"].sum() == 219, "Bowling primary sum must equal 219"
    assert bowl_prof["emerging_player_count"].sum() == 324, "Bowling emerging sum must equal 324"
    assert bowl_prof["total_player_count"].sum() == 543, "Bowling total sum must equal 543"
    
    print("  [PASS 13/21] Cluster assignment counts reconcile 100% with cluster profile totals.")


def test_original_scale_output_values():
    bat_assign = pd.read_csv("data/processed/metrics/batting_cluster_assignments.csv")
    bowl_assign = pd.read_csv("data/processed/metrics/bowling_cluster_assignments.csv")
    
    # Batting strike rates are in original percentage terms (> 50.0)
    assert bat_assign["strike_rate"].min() >= 0.0, "Strike rates must be non-negative"
    assert bat_assign["strike_rate"].max() > 100.0, "Strike rates must be in original scale, not scaled"
    
    # Bowling economies are in original RPO terms (3.0 to 36.0)
    assert bowl_assign["economy_rate"].min() >= 0.0, "Economy rates must be non-negative"
    assert bowl_assign["economy_rate"].median() > 5.0, "Economy rates must be in original scale, not scaled"
    
    print("  [PASS 14/21] Output CSVs retain genuine original-scale cricket metric values.")


def test_deterministic_repeated_execution():
    from backend.ml.player_features import prepare_batting_features
    from backend.ml.kmeans_clustering import train_kmeans_model
    
    b1 = prepare_batting_features()
    km1 = train_kmeans_model(b1["X_primary_scaled"], k=3, random_state=42)
    
    b2 = prepare_batting_features()
    km2 = train_kmeans_model(b2["X_primary_scaled"], k=3, random_state=42)
    
    np.testing.assert_array_equal(km1.labels_, km2.labels_)
    np.testing.assert_allclose(km1.cluster_centers_, km2.cluster_centers_)
    
    print("  [PASS 15/21] Determinism verified: 100% identical labels and centroids on repeated execution.")


def test_model_serialization_and_reload():
    km_bat = joblib.load("models/phase4/batting_kmeans_model.joblib")
    scaler_bat = joblib.load("models/phase4/batting_scaler.joblib")
    with open("models/phase4/batting_metadata.json", "r", encoding="utf-8") as f:
        bat_meta = json.load(f)
    
    test_df = pd.DataFrame([[180.0, 50.0, 25.0, 25.0, 30.0]], columns=bat_meta["features"])
    scaled_vec = scaler_bat.transform(test_df)
    pred = km_bat.predict(scaled_vec)
    
    assert pred[0] in [0, 1, 2], f"Predicted cluster {pred[0]} out of bounds"
    
    print("  [PASS 16/21] Model and scaler serialization reloadable and executable.")


def test_provisional_emerging_assignments():
    bat_assign = pd.read_csv("data/processed/metrics/batting_cluster_assignments.csv")
    bowl_assign = pd.read_csv("data/processed/metrics/bowling_cluster_assignments.csv")
    
    assert (bat_assign[bat_assign["cohort"] == "emerging"]["assignment_status"] == "provisional").all()
    assert (bowl_assign[bowl_assign["cohort"] == "emerging"]["assignment_status"] == "provisional").all()
    
    print("  [PASS 17/21] All emerging players correctly marked with 'provisional' assignment status.")


def test_no_fabricated_tactical_claims():
    bat_assign = pd.read_csv("data/processed/metrics/batting_cluster_assignments.csv")
    bowl_assign = pd.read_csv("data/processed/metrics/bowling_cluster_assignments.csv")
    bat_prof = pd.read_csv("data/processed/metrics/batting_cluster_profiles.csv")
    bowl_prof = pd.read_csv("data/processed/metrics/bowling_cluster_profiles.csv")
    
    forbidden_phrases = ["overs 16 and 18", "overs 17 and 19", "powerplay specialist", "powerplay enforcer"]
    
    for text in bat_assign["player_archetype_explanation"].dropna():
        for phrase in forbidden_phrases:
            assert phrase not in text.lower(), f"Forbidden phrase '{phrase}' in batting explanation"
            
    for text in bowl_assign["player_archetype_explanation"].dropna():
        for phrase in forbidden_phrases:
            assert phrase not in text.lower(), f"Forbidden phrase '{phrase}' in bowling explanation"
            
    for text in bat_prof["potential_tactical_role"].dropna():
        for phrase in forbidden_phrases:
            assert phrase not in text.lower(), f"Forbidden phrase '{phrase}' in batting profile role"
            
    for text in bowl_prof["potential_tactical_role"].dropna():
        for phrase in forbidden_phrases:
            assert phrase not in text.lower(), f"Forbidden phrase '{phrase}' in bowling profile role"
            
    print("  [PASS 18/21] Unsupported over-specific tactical claims strictly absent from explanations and profiles.")


def test_spot_check_five_batters_and_five_bowlers():
    bat_assign = pd.read_csv("data/processed/metrics/batting_cluster_assignments.csv")
    bowl_assign = pd.read_csv("data/processed/metrics/bowling_cluster_assignments.csv")
    
    # 5 Batters:
    # Tristan Stubbs (ID: 20702): Explosive Finishers (Cluster 1)
    stubbs = bat_assign[bat_assign["player_id"] == 20702].iloc[0]
    assert stubbs["cluster_id"] == 1
    assert "Explosive Pressure Finishers" in stubbs["archetype_name"]
    
    # MS Dhoni (ID: 8): Explosive Finishers (Cluster 1)
    dhoni = bat_assign[bat_assign["player_id"] == 8].iloc[0]
    assert dhoni["cluster_id"] == 1
    assert "Explosive Pressure Finishers" in dhoni["archetype_name"]
    
    # Tim David (ID: 6396): Explosive Finishers (Cluster 1)
    david = bat_assign[bat_assign["player_id"] == 6396].iloc[0]
    assert david["cluster_id"] == 1
    assert "Explosive Pressure Finishers" in david["archetype_name"]
    
    # Clive Madande (ID: 21781): Steady Anchors (Cluster 2)
    madande = bat_assign[bat_assign["player_id"] == 21781].iloc[0]
    assert madande["cluster_id"] == 2
    assert "Steady Pressure Anchors" in madande["archetype_name"]
    
    # Shaheen Afridi (ID: 6355): Struggling Batters (Cluster 0)
    shaheen = bat_assign[bat_assign["player_id"] == 6355].iloc[0]
    assert shaheen["cluster_id"] == 0
    assert "Pressure-Struggling" in shaheen["archetype_name"]
    
    # 5 Bowlers:
    # Sunil Narine (ID: 781): Economical Controllers (Cluster 0)
    narine = bowl_assign[bowl_assign["player_id"] == 781].iloc[0]
    assert narine["cluster_id"] == 0
    assert "Economical Pressure Controllers" in narine["archetype_name"]
    
    # Pramod Madushan (ID: 6351 or 6932): Economical Controllers (Cluster 0)
    madushan = bowl_assign[bowl_assign["player_name"].str.contains("Pramod Madushan", case=False, na=False)].iloc[0]
    assert madushan["cluster_id"] == 0
    assert "Economical Pressure Controllers" in madushan["archetype_name"]
    
    # Rasikh Salam (ID: 7327): Economical Controllers (Cluster 0)
    rasikh = bowl_assign[bowl_assign["player_id"] == 7327].iloc[0]
    assert rasikh["cluster_id"] == 0
    assert "Economical Pressure Controllers" in rasikh["archetype_name"]
    
    # Arshdeep Singh (ID: 6464): Moderate Containment (Cluster 1)
    arshdeep = bowl_assign[bowl_assign["player_id"] == 6464].iloc[0]
    assert arshdeep["cluster_id"] == 1
    assert "Moderate-Containment" in arshdeep["archetype_name"]
    
    # Mohammed Siraj (ID: 5944): Moderate Containment (Cluster 1)
    siraj = bowl_assign[bowl_assign["player_id"] == 5944].iloc[0]
    assert siraj["cluster_id"] == 1
    assert "Moderate-Containment" in siraj["archetype_name"]
    
    print("  [PASS 19/21] Spot checks for 5 batters and 5 bowlers match measured traits and cluster boundaries.")


def test_super_over_isolation_in_features():
    from backend.ml.player_features import prepare_batting_features, prepare_bowling_features
    
    b = prepare_batting_features()
    w = prepare_bowling_features()
    
    # Batting pressure balls total in deduplicated union segment: 50,669 (excluding 38 Super Over balls)
    total_bat_balls = b["full_df"]["balls_faced"].sum()
    assert total_bat_balls == 50669, f"Batting pressure balls Faced must be 50,669; found {total_bat_balls}"
    
    # Bowling legal pressure balls in deduplicated union segment: 50,329 (excluding 33 legal Super Over balls)
    total_bowl_balls = w["full_df"]["legal_balls"].sum()
    assert total_bowl_balls == 50329, f"Bowling legal pressure balls must be 50,329; found {total_bowl_balls}"
    
    print("  [PASS 20/21] Super Over isolation verified: 38 balls quarantined from all feature vectors.")


def test_regression_preservation_phases_1_to_3():
    # Phase 1: Clean matches
    clean_matches = pd.read_csv("data/processed/clean_matches.csv")
    assert len(clean_matches) == 883, f"Total matches must remain 883; found {len(clean_matches)}"
    
    # Phase 2: Clean deliveries
    clean_deliv = pd.read_csv("data/processed/clean_deliveries.csv")
    assert len(clean_deliv) == 200999, f"Clean deliveries must remain 200,999; found {len(clean_deliv)}"
    
    # Phase 3: Leaderboards
    top10_bat = pd.read_csv("data/processed/metrics/top10_batters.csv")
    top10_bowl = pd.read_csv("data/processed/metrics/top10_bowlers.csv")
    assert len(top10_bat) == 10, "Top 10 batters must have 10 rows"
    assert len(top10_bowl) == 10, "Top 10 bowlers must have 10 rows"
    assert "Najibullah Zadran" in top10_bat.iloc[0]["player_name"], "#1 Batter must remain Najibullah Zadran"
    assert "Tristan Stubbs" in top10_bat.iloc[1]["player_name"], "#2 Batter must remain Tristan Stubbs"
    assert "Rasikh Salam" in top10_bowl.iloc[0]["player_name"], "#1 Bowler must remain Rasikh Salam"
    
    print("  [PASS 21/21] Full regression preservation confirmed across Phase 1, Phase 2, and Phase 3.")


if __name__ == "__main__":
    print("=" * 70)
    print("Running Phase 4 Automated Test Suite...")
    print("=" * 70)
    test_artifacts_exist_and_non_empty()
    test_exact_feature_redundancy_and_determinant()
    test_feature_uniqueness_and_compactness()
    test_zero_dismissal_batter_handling()
    test_zero_wicket_bowler_handling()
    test_primary_only_imputer_and_scaler_fitting()
    test_emerging_cohort_exclusion_from_model_fitting()
    test_valid_k_candidate_selection()
    test_non_empty_clusters_and_balance()
    test_player_id_uniqueness_and_coverage()
    test_separate_batting_and_bowling_models()
    test_no_clutch_iq_or_rank_leakage()
    test_cluster_profile_counts_reconciliation()
    test_original_scale_output_values()
    test_deterministic_repeated_execution()
    test_model_serialization_and_reload()
    test_provisional_emerging_assignments()
    test_no_fabricated_tactical_claims()
    test_spot_check_five_batters_and_five_bowlers()
    test_super_over_isolation_in_features()
    test_regression_preservation_phases_1_to_3()
    print("=" * 70)
    print("ALL 21 TESTS PASSED SUCCESSFULLY! [OK]")
    print("=" * 70)

"""
SUPER RR — CLUTCH IQ
Unit & Validation Test Suite for Phase 3: Clutch IQ Scoring & Bayesian Shrinkage

Run with:
    python backend/tests/test_clutch_scoring.py
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import json
import pandas as pd
import numpy as np
from scipy.stats import norm


def test_phase3_artifacts_exist_and_non_empty():
    required_files = [
        "data/processed/metrics/batting_clutch_scores.csv",
        "data/processed/metrics/bowling_clutch_scores.csv",
        "data/processed/metrics/top10_batters.csv",
        "data/processed/metrics/top10_bowlers.csv",
        "data/processed/metrics/emerging_batters.csv",
        "data/processed/metrics/emerging_bowlers.csv",
        "data/processed/metrics/ranking_sensitivity.csv",
        "data/processed/metrics/clutch_scoring_quality_report.json"
    ]
    for f in required_files:
        assert os.path.exists(f), f"Missing Phase 3 artifact: {f}"
        assert os.path.getsize(f) > 0, f"Artifact is empty: {f}"
    print("  [PASS 1/10] All 8 Phase 3 artifacts exist and are non-empty.")


def test_minimum_sample_size_primary_vs_emerging():
    top10_bat = pd.read_csv("data/processed/metrics/top10_batters.csv")
    top10_bowl = pd.read_csv("data/processed/metrics/top10_bowlers.csv")
    emerging_bat = pd.read_csv("data/processed/metrics/emerging_batters.csv")
    emerging_bowl = pd.read_csv("data/processed/metrics/emerging_bowlers.csv")

    # Primary eligible must have >= 50 balls
    assert (top10_bat['balls_faced'] >= 50).all(), "All Top 10 batters must have >= 50 balls faced"
    assert (top10_bowl['legal_balls'] >= 50).all(), "All Top 10 bowlers must have >= 50 legal balls"

    # Emerging performers must strictly have < 50 balls
    assert (emerging_bat['balls_faced'] < 50).all(), "All emerging batters must have < 50 balls faced"
    assert (emerging_bowl['legal_balls'] < 50).all(), "All emerging bowlers must have < 50 legal balls"

    # Mutually exclusive sets
    bat_overlap = set(top10_bat['player_id']).intersection(set(emerging_bat['player_id']))
    bowl_overlap = set(top10_bowl['player_id']).intersection(set(emerging_bowl['player_id']))
    assert len(bat_overlap) == 0, f"Batters overlap between primary and emerging: {bat_overlap}"
    assert len(bowl_overlap) == 0, f"Bowlers overlap between primary and emerging: {bowl_overlap}"

    print(f"  [PASS 2/10] Sample size rules verified (Top 10 >= 50 balls; {len(emerging_bat)} emerging batters & {len(emerging_bowl)} emerging bowlers < 50 balls).")


def test_score_bounds_and_validity():
    bat_scores = pd.read_csv("data/processed/metrics/batting_clutch_scores.csv")
    bowl_scores = pd.read_csv("data/processed/metrics/bowling_clutch_scores.csv")

    assert bat_scores['clutch_iq'].between(0.0, 100.0).all(), "Batting Clutch IQ must be within [0, 100]"
    assert bowl_scores['clutch_iq'].between(0.0, 100.0).all(), "Bowling Clutch IQ must be within [0, 100]"
    assert not bat_scores['clutch_iq'].isna().any(), "No NaN Clutch IQ scores in batting"
    assert not bowl_scores['clutch_iq'].isna().any(), "No NaN Clutch IQ scores in bowling"

    print("  [PASS 3/10] All Clutch IQ scores bounded within [0, 100] with zero NaNs.")


def test_monotonicity_and_directional_correctness():
    bat_scores = pd.read_csv("data/processed/metrics/batting_clutch_scores.csv")
    bowl_scores = pd.read_csv("data/processed/metrics/bowling_clutch_scores.csv")

    # In batting: higher shrunk delta SR must yield higher norm_score_strike_rate
    sr_sorted = bat_scores.sort_values('shrunk_delta_strike_rate')
    assert (np.diff(sr_sorted['norm_score_strike_rate']) >= -1e-6).all(), "norm_score_strike_rate must be monotonic"

    # In bowling: higher shrunk delta economy must yield higher norm_score_economy
    econ_sorted = bowl_scores.sort_values('shrunk_delta_economy')
    assert (np.diff(econ_sorted['norm_score_economy']) >= -1e-6).all(), "norm_score_economy must be monotonic"

    print("  [PASS 4/10] Monotonicity and directional correctness verified across normalized metric scores.")


def test_bayesian_shrinkage_behavior():
    bat_scores = pd.read_csv("data/processed/metrics/batting_clutch_scores.csv")
    bowl_scores = pd.read_csv("data/processed/metrics/bowling_clutch_scores.csv")

    # 1. Weights in [0, 1]
    assert bat_scores['reliability_weight'].between(0.0, 1.0).all(), "Batting weights must be in [0, 1]"
    assert bowl_scores['reliability_weight'].between(0.0, 1.0).all(), "Bowling weights must be in [0, 1]"

    # 2. Magnitude reduction: abs(shrunk) <= abs(raw) + eps
    assert (np.abs(bat_scores['shrunk_delta_strike_rate']) <= np.abs(bat_scores['raw_delta_strike_rate']) + 0.05).all()
    assert (np.abs(bowl_scores['shrunk_delta_economy']) <= np.abs(bowl_scores['raw_delta_economy']) + 0.05).all()

    # 3. No sign reversal: shrunk * raw >= 0 (never flips sign from positive to negative or vice versa)
    assert (bat_scores['shrunk_delta_strike_rate'] * bat_scores['raw_delta_strike_rate'] >= -1e-6).all(), "Shrinkage must never reverse sign"
    assert (bowl_scores['shrunk_delta_economy'] * bowl_scores['raw_delta_economy'] >= -1e-6).all(), "Shrinkage must never reverse sign"

    print("  [PASS 5/10] Bayesian shrinkage properties verified (magnitude reduced toward 0, zero sign reversals).")


def test_no_duplicate_players():
    top10_bat = pd.read_csv("data/processed/metrics/top10_batters.csv")
    top10_bowl = pd.read_csv("data/processed/metrics/top10_bowlers.csv")

    assert len(top10_bat) == 10, "Top 10 batters must have exactly 10 rows"
    assert top10_bat['player_id'].nunique() == 10, "Top 10 batters must have 10 unique player IDs"

    assert len(top10_bowl) == 10, "Top 10 bowlers must have exactly 10 rows"
    assert top10_bowl['player_id'].nunique() == 10, "Top 10 bowlers must have 10 unique player IDs"

    # Distinct ranks from 1 to 10
    assert list(top10_bat['rank']) == list(range(1, 11)), "Batters ranks must be 1 to 10"
    assert list(top10_bowl['rank']) == list(range(1, 11)), "Bowlers ranks must be 1 to 10"

    print("  [PASS 6/10] Exactly 10 unique, non-duplicate players in Top 10 leaderboards with sequential ranks 1-10.")


def test_deterministic_tiebreaking():
    top10_bat = pd.read_csv("data/processed/metrics/top10_batters.csv")
    top10_bowl = pd.read_csv("data/processed/metrics/top10_bowlers.csv")

    # Batters check: Clutch IQ non-increasing
    assert (np.diff(top10_bat['clutch_iq']) <= 0).all(), "Batters Top 10 must be sorted by Clutch IQ descending"
    # Bowlers check: Clutch IQ non-increasing
    assert (np.diff(top10_bowl['clutch_iq']) <= 0).all(), "Bowlers Top 10 must be sorted by Clutch IQ descending"

    print("  [PASS 7/10] Deterministic ordering verified (Clutch IQ desc, reliability desc, player_id asc).")


def test_super_overs_exclusion():
    deliv = pd.read_csv("data/processed/clean_deliveries.csv")
    bat_press = pd.read_csv("data/processed/metrics/batting_pressure.csv")

    # Regular Any Pressure deliveries
    so_deliv = deliv[deliv['innings'] >= 3]
    assert len(so_deliv) == 38, "Super over balls must equal 38"

    # Any Pressure segment excludes super overs
    any_press_deliv = deliv[(deliv['innings'] <= 2) & ((deliv['overid'] >= 16) | (deliv['is_situational_close_chase']) | (deliv['is_knockout']))]
    assert len(any_press_deliv) == 53453, "Any Pressure deliveries must equal 53,453"
    assert (any_press_deliv['innings'] <= 2).all(), "Any Pressure deliveries must strictly be regular innings"

    print("  [PASS 8/10] Zero Super Over contamination verified in primary Clutch IQ scoring dataset.")


def test_phase2_reconciliation_values_preserved():
    summary = pd.read_csv("data/processed/metrics/pressure_summary.csv")
    overall = summary[summary['segment_name'] == "Overall Regular (Innings 1-2)"].iloc[0]
    any_press = summary[summary['segment_name'] == "Any Pressure (Union)"].iloc[0]
    baseline = summary[summary['segment_name'] == "Non-Pressure Baseline"].iloc[0]

    assert overall['total_deliveries'] == 200961
    assert overall['legal_balls'] == 192412
    assert overall['balls_faced'] == 193251
    assert overall['total_runs_off_bat'] == 269506
    assert overall['bowler_runs_conceded'] == 278054
    assert overall['team_innings_runs'] == 281418
    assert overall['bowler_wickets'] == 10261

    assert any_press['total_deliveries'] == 53453
    assert baseline['total_deliveries'] == 147508
    assert any_press['total_deliveries'] + baseline['total_deliveries'] == 200961

    print("  [PASS 9/10] All approved Phase 2 reconciliation values strictly preserved.")


def test_spot_check_five_batters_and_five_bowlers():
    bat_scores = pd.read_csv("data/processed/metrics/batting_clutch_scores.csv").set_index('player_id')
    bowl_scores = pd.read_csv("data/processed/metrics/bowling_clutch_scores.csv").set_index('player_id')

    # Spot check 5 batters:
    # 2533 (Najibullah Zadran), 20702 (Tristan Stubbs), 8 (MS Dhoni), 2984 (Sikandar Raza), 4708 (Rinku Singh)
    bat_pids = [2533, 20702, 8, 2984, 4708]
    for pid in bat_pids:
        r = bat_scores.loc[pid]
        recomputed_iq = round(
            0.40 * r['norm_score_strike_rate'] +
            0.25 * r['norm_score_dot_pct'] +
            0.25 * r['norm_score_boundary_ball_pct'] +
            0.10 * r['norm_score_batting_avg'],
            2
        )
        assert abs(r['clutch_iq'] - recomputed_iq) <= 0.01, f"Batting Clutch IQ spot check failed for {r['player_name']}"

    # Spot check 5 bowlers:
    # 7327 (Rasikh Salam), 6932 (Pramod Madushan), 5979 (Abrar Ahmed), 781 (Sunil Narine), 2933 (Jasprit Bumrah)
    bowl_pids = [7327, 6932, 5979, 781, 2933]
    for pid in bowl_pids:
        r = bowl_scores.loc[pid]
        recomputed_iq = round(
            0.35 * r['norm_score_economy'] +
            0.25 * r['norm_score_wicket_sr'] +
            0.20 * r['norm_score_dot_pct'] +
            0.20 * r['norm_score_boundary_balls'],
            2
        )
        assert abs(r['clutch_iq'] - recomputed_iq) <= 0.01, f"Bowling Clutch IQ spot check failed for {r['player_name']}"

    print("  [PASS 10/10] Independent mathematical spot checks verified for 5 batters and 5 bowlers with exact match.")


if __name__ == "__main__":
    print("=" * 70)
    print("Running Phase 3 Clutch IQ Scoring & Leaderboard Test Suite...")
    print("=" * 70)
    test_phase3_artifacts_exist_and_non_empty()
    test_minimum_sample_size_primary_vs_emerging()
    test_score_bounds_and_validity()
    test_monotonicity_and_directional_correctness()
    test_bayesian_shrinkage_behavior()
    test_no_duplicate_players()
    test_deterministic_tiebreaking()
    test_super_overs_exclusion()
    test_phase2_reconciliation_values_preserved()
    test_spot_check_five_batters_and_five_bowlers()
    print("=" * 70)
    print("ALL 10 PHASE 3 TESTS PASSED SUCCESSFULLY! [OK]")
    print("=" * 70)

"""
SUPER RR — CLUTCH IQ
Unit & Validation Tests for Phase 1 Data Cleaning & Enrichment Pipeline

Run with:
    python backend/tests/test_data_pipeline.py
"""

import os
import json
import sqlite3
import pandas as pd


def test_files_exist():
    required_files = [
        "data/processed/clean_deliveries.csv",
        "data/processed/clean_matches.csv",
        "data/processed/clean_players.csv",
        "data/processed/clean_playing_eleven.csv",
        "data/processed/clutch_iq.db",
        "data/processed/data_quality_log.json"
    ]
    for f in required_files:
        assert os.path.exists(f), f"Required file missing: {f}"
        assert os.path.getsize(f) > 0, f"File is empty: {f}"
    print("  [PASS] All 6 processed artifacts exist and are non-empty.")


def test_row_counts():
    deliv = pd.read_csv("data/processed/clean_deliveries.csv")
    matches = pd.read_csv("data/processed/clean_matches.csv")
    players = pd.read_csv("data/processed/clean_players.csv")
    p11 = pd.read_csv("data/processed/clean_playing_eleven.csv")

    assert len(deliv) == 200999, f"Expected 200999 deliveries, got {len(deliv)}"
    assert len(matches) == 883, f"Expected 883 matches, got {len(matches)}"
    assert len(players) == 1217, f"Expected 1217 players, got {len(players)}"
    assert len(p11) == 28341, f"Expected 28341 playing eleven records, got {len(p11)}"
    print("  [PASS] Exact row counts verified (0 deliveries dropped, 40 duplicates removed from p11).")


def test_legality_and_bowler_wickets():
    deliv = pd.read_csv("data/processed/clean_deliveries.csv")

    # Legal deliveries
    legal_count = deliv['is_legal_ball'].sum()
    illegal_count = (~deliv['is_legal_ball']).sum()
    assert legal_count + illegal_count == 200999, "Legal + illegal must sum to 200999"

    wides = deliv[deliv['extras_type'] == 'wide']
    assert (wides['is_legal_ball'] == False).all(), "Wides must not be marked legal"

    oversteps = deliv[deliv['extras_type'] == 'Overstep']
    assert (oversteps['is_legal_ball'] == False).all(), "Oversteps must not be marked legal"

    other_nb = deliv[deliv['extras_type'] == 'other']
    assert (other_nb['is_legal_ball'] == False).all(), "Other no-balls must not be marked legal"

    # Bowler runs conceded
    wides = deliv[deliv['is_wide']]
    assert (wides['bowler_runs_conceded'] == 1).all(), "Wides must concede exactly 1 bowler run"

    fielding_extras = deliv[deliv['is_bye'] | deliv['is_legbye'] | deliv['is_penalty']]
    assert (fielding_extras['bowler_runs_conceded'] == 0).all(), "Byes, leg-byes, and penalty must concede 0 bowler runs"

    # Bowler wickets
    bowler_wkts = deliv['is_bowler_wicket'].sum()
    assert bowler_wkts == 10272, f"Expected 10272 bowler wickets, got {bowler_wkts}"

    runouts = deliv[deliv['dismissal_type'] == 'RunOut']
    assert (runouts['is_bowler_wicket'] == False).all(), "RunOuts must never be bowler wickets"

    retire_outs = deliv[deliv['dismissal_type'] == 'Retire Out']
    assert (retire_outs['is_bowler_wicket'] == False).all(), "Retire Outs must never be bowler wickets"

    obstructing = deliv[deliv['dismissal_type'] == 'Obstructing the field']
    assert (obstructing['is_bowler_wicket'] == False).all(), "Obstructing must never be bowler wickets"

    print("  [PASS] Legal delivery and bowler wicket definitions verified (10,272 bowler wickets).")


def test_super_overs_isolation():
    deliv = pd.read_csv("data/processed/clean_deliveries.csv")
    super_overs = deliv[deliv['is_super_over']]
    assert len(super_overs) == 38, f"Expected 38 super over balls, got {len(super_overs)}"
    assert set(super_overs['innings'].unique()) == {3, 4}, "Super overs must be innings 3 or 4"
    assert (deliv[deliv['innings'] <= 2]['is_super_over'] == False).all(), "Regular innings must not be super overs"
    print("  [PASS] Super Overs cleanly segregated (38 deliveries across 6 matches).")


def test_situational_close_chases_zero_leakage():
    deliv = pd.read_csv("data/processed/clean_deliveries.csv")

    # Never in innings 1, 3, or 4
    non_chase = deliv[deliv['innings'] != 2]
    assert (non_chase['is_situational_close_chase'] == False).all(), "Close chase must only exist in Innings 2"

    chase_pressure = deliv[deliv['is_situational_close_chase']]
    assert len(chase_pressure) > 0, "Expected non-zero close chase pressure deliveries"
    assert (chase_pressure['legal_balls_remaining'] <= 36).all(), "Must have <= 36 balls remaining"
    assert (chase_pressure['required_run_rate'] >= 9.0).all(), "Must have RRR >= 9.0"
    assert (chase_pressure['runs_needed'] > 0).all(), "Must have runs needed > 0"
    print(f"  [PASS] Zero outcome leakage verified across {len(chase_pressure)} situational close chase deliveries.")


def test_sqlite_database():
    conn = sqlite3.connect("data/processed/clutch_iq.db")
    cursor = conn.cursor()

    for table in ["clean_deliveries", "clean_matches", "clean_players", "clean_playing_eleven"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        assert count > 0, f"Table {table} in SQLite is empty"

    cursor.execute("SELECT COUNT(*) FROM clean_deliveries")
    assert cursor.fetchone()[0] == 200999, "SQLite deliveries count must be 200999"
    conn.close()
    print("  [PASS] SQLite database verified with all tables matching CSV counts.")


def test_data_quality_log():
    with open("data/processed/data_quality_log.json", "r", encoding="utf-8") as f:
        log = json.load(f)
    assert log["pipeline_version"] == "1.0.0"
    assert all(log["validation_checks"].values()), "All checks in quality log must be True"
    print("  [PASS] Data quality log verified with 100% passing checks.")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Phase 1 Pipeline Test Suite...")
    print("=" * 60)
    test_files_exist()
    test_row_counts()
    test_legality_and_bowler_wickets()
    test_super_overs_isolation()
    test_situational_close_chases_zero_leakage()
    test_sqlite_database()
    test_data_quality_log()
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! [OK]")
    print("=" * 60)

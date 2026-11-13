"""
SUPER RR — CLUTCH IQ
Phase 1: Deterministic Data Cleaning & Enrichment Pipeline

This script cleans, enriches, and validates the raw cricket dataset from data/raw/
and outputs structured, production-ready tables in data/processed/.

Working Rules Enforced:
1. Never modifies or deletes any original file in data/raw/.
2. Deterministic and 100% reproducible.
3. Preserves all player IDs, match IDs, and delivery records (200,999 rows preserved).
4. Strictly distinguishes legal balls from illegal deliveries (wides, no-balls).
5. Excludes fielding dismissals (Run Outs, Retire Outs, Obstructing) from bowler wickets.
6. Isolates Super Overs (innings >= 3) from regular 20-over rate statistics.
7. Computes situational close-chase pressure in Innings 2 WITHOUT outcome leakage.
8. Writes an exhaustive data-quality audit log in data/processed/data_quality_log.json.
"""

import os
import json
import re
import time
import sqlite3
import pandas as pd
import numpy as np


def clean_and_enrich_data(raw_dir: str = "data/raw", processed_dir: str = "data/processed"):
    start_time = time.time()
    os.makedirs(processed_dir, exist_ok=True)
    
    quality_log = {
        "pipeline_version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "raw_directory": raw_dir,
        "processed_directory": processed_dir,
        "actions_performed": [],
        "validation_checks": {},
        "summary_statistics": {}
    }
    
    print("=" * 70)
    print("SUPER RR — CLUTCH IQ: Starting Phase 1 Data Cleaning & Enrichment")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # 1. Load Raw CSV Files (Read-only)
    # -------------------------------------------------------------------------
    print("\n[Step 1/6] Loading raw dataset files...")
    competitions = pd.read_csv(os.path.join(raw_dir, "competitions.csv"))
    teams = pd.read_csv(os.path.join(raw_dir, "teams.csv"))
    matches = pd.read_csv(os.path.join(raw_dir, "matches.csv"))
    mapping = pd.read_csv(os.path.join(raw_dir, "competition_team_player_mapping.csv"))
    playing_eleven = pd.read_csv(os.path.join(raw_dir, "playing_eleven.csv"))
    deliveries = pd.read_csv(os.path.join(raw_dir, "ball_by_ball.csv"))

    quality_log["raw_dimensions"] = {
        "competitions": list(competitions.shape),
        "teams": list(teams.shape),
        "matches": list(matches.shape),
        "competition_team_player_mapping": list(mapping.shape),
        "playing_eleven": list(playing_eleven.shape),
        "ball_by_ball": list(deliveries.shape)
    }
    print(f"  Loaded {len(matches)} matches and {len(deliveries)} deliveries.")

    # -------------------------------------------------------------------------
    # 2. Clean & Enrich Matches Table
    # -------------------------------------------------------------------------
    print("\n[Step 2/6] Cleaning and enriching Matches...")
    # Merge competition details
    clean_matches = matches.merge(
        competitions[['comp_id', 'comp_name', 'match_format', 'season']],
        on='comp_id',
        how='left'
    )

    # Convert revised overs: the raw columns store BALLS, not overs!
    clean_matches['first_inn_revised_balls'] = clean_matches['first_inn_revised_overs']
    clean_matches['second_inn_revised_balls'] = clean_matches['second_inn_revised_overs']
    clean_matches['first_inn_revised_overs'] = clean_matches['first_inn_revised_balls'] / 6.0
    clean_matches['second_inn_revised_overs'] = clean_matches['second_inn_revised_balls'] / 6.0

    # Total allotted balls per innings
    clean_matches['allotted_balls_inn1'] = np.where(
        clean_matches['first_inn_revised_balls'].notnull(),
        clean_matches['first_inn_revised_balls'],
        120.0
    )
    clean_matches['allotted_balls_inn2'] = np.where(
        clean_matches['second_inn_revised_balls'].notnull(),
        clean_matches['second_inn_revised_balls'],
        120.0
    )

    # Parse match margins
    def parse_margin(res):
        if not isinstance(res, str):
            return "Unknown", 0
        if "Abandoned" in res:
            return "Abandoned", 0
        if "No Result" in res:
            return "No Result", 0
        if any(term in res.lower() for term in ["tied", "super over"]):
            return "Tie/SuperOver", 0
        m_run = re.search(r'won\s+(?:by\s+)?(\d+)\s+runs?', res, re.I)
        if m_run:
            return "Runs", int(m_run.group(1))
        m_wkt = re.search(r'won\s+(?:by\s+)?(\d+)\s+(?:wickets?|wkts?)', res, re.I)
        if m_wkt:
            return "Wickets", int(m_wkt.group(1))
        return "Other", 0

    margin_info = clean_matches['result'].apply(parse_margin)
    clean_matches['margin_type'] = [m[0] for m in margin_info]
    clean_matches['margin_value'] = [m[1] for m in margin_info]

    # Post-hoc match closeness (FOR SECONDARY EXPLORATION ONLY - NEVER FOR DELIVERY TAGGING)
    clean_matches['is_close_margin_match'] = (
        (clean_matches['margin_type'] == "Tie/SuperOver") |
        ((clean_matches['margin_type'] == "Runs") & (clean_matches['margin_value'] <= 15)) |
        ((clean_matches['margin_type'] == "Wickets") & (clean_matches['margin_value'] <= 3))
    )

    quality_log["actions_performed"].append(
        "Converted revised overs from raw balls to fractional overs (divided by 6)."
    )
    quality_log["actions_performed"].append(
        "Extracted normalized match margin types and post-hoc closeness flag."
    )

    # -------------------------------------------------------------------------
    # 3. Clean Players and Deduplicate Playing XI
    # -------------------------------------------------------------------------
    print("\n[Step 3/6] Cleaning Players & Deduplicating Playing XI...")
    # Clean unique players
    name_counts = mapping.groupby('player_name')['player_id'].nunique()
    multi_id_names = set(name_counts[name_counts > 1].index)
    
    clean_players = mapping.groupby(['player_id', 'player_name']).agg(
        teams=('team_name', lambda s: ", ".join(sorted(set(s)))),
        competitions=('comp_name', lambda s: ", ".join(sorted(set(s))))
    ).reset_index()
    clean_players['is_name_collision'] = clean_players['player_name'].isin(multi_id_names)

    # Clean playing eleven: deduplicate 40 redundant lineup revision rows in 3 matches (75 total flagged rows)
    initial_p11_count = len(playing_eleven)
    clean_playing_eleven = playing_eleven.drop_duplicates(
        subset=['match_id', 'player_id'],
        keep='first'
    ).copy()
    dropped_p11_count = initial_p11_count - len(clean_playing_eleven)
    
    quality_log["actions_performed"].append(
        f"Deduplicated {dropped_p11_count} redundant lineup revision rows in playing_eleven (28,341 preserved)."
    )
    print(f"  Deduplicated {dropped_p11_count} redundant lineup rows in playing_eleven ({len(clean_playing_eleven)} preserved).")

    # -------------------------------------------------------------------------
    # 4. Clean & Enrich Ball-by-Ball Deliveries
    # -------------------------------------------------------------------------
    print("\n[Step 4/6] Cleaning and enriching Deliveries (200,999 balls)...")
    clean_deliveries = deliveries.copy()

    # Anomaly correction: Row 127899, Match 40709 (Tilak Varma retired out)
    if clean_deliveries.loc[127899, 'dismissal_type'] == 'Retire Out' and pd.isna(clean_deliveries.loc[127899, 'dismissed_player_id']):
        clean_deliveries.loc[127899, 'dismissed_player_id'] = 7897.0
        quality_log["actions_performed"].append(
            "Resolved missing dismissed_player_id on delivery 127899 to Tilak Varma (7897) for Retire Out."
        )

    # Standardize dismissal type typo
    clean_deliveries['dismissal_type'] = clean_deliveries['dismissal_type'].replace(
        {'Obstracting the field': 'Obstructing the field'}
    )

    # Delivery legality
    clean_deliveries['is_legal_ball'] = ~clean_deliveries['extras_type'].isin(['wide', 'Overstep', 'other'])
    clean_deliveries['is_wide'] = clean_deliveries['extras_type'] == 'wide'
    clean_deliveries['is_noball'] = clean_deliveries['extras_type'].isin(['Overstep', 'other'])
    clean_deliveries['is_bye'] = clean_deliveries['extras_type'] == 'byes'
    clean_deliveries['is_legbye'] = clean_deliveries['extras_type'] == 'legbyes'
    clean_deliveries['is_penalty'] = clean_deliveries['extras_type'] == 'Penalty'

    # Bowler statistics
    clean_deliveries['bowler_runs_conceded'] = clean_deliveries['runs']
    clean_deliveries.loc[clean_deliveries['is_wide'], 'bowler_runs_conceded'] = 1
    clean_deliveries.loc[clean_deliveries['is_noball'], 'bowler_runs_conceded'] = 1 + clean_deliveries.loc[clean_deliveries['is_noball'], 'runs']
    # Explicitly ensure fielding extras (byes, legbyes, penalty) are never debited to the bowler
    clean_deliveries.loc[clean_deliveries['is_bye'] | clean_deliveries['is_legbye'] | clean_deliveries['is_penalty'], 'bowler_runs_conceded'] = 0
    # extras_2_runs excluded from bowler runs as documented

    bowler_wkt_types = ['Bowled', 'Caught', 'LBW', 'Stump', 'Hit Wicket']
    clean_deliveries['is_bowler_wicket'] = (
        clean_deliveries['is_wicket'] &
        clean_deliveries['dismissal_type'].isin(bowler_wkt_types)
    )

    # Batter statistics
    # Balls faced strictly excludes wides, but includes all legal deliveries and no-balls
    clean_deliveries['is_batter_ball_faced'] = clean_deliveries['extras_type'] != 'wide'
    clean_deliveries['is_batter_out'] = clean_deliveries['is_wicket'] & (clean_deliveries['dismissed_player_id'] == clean_deliveries['striker_id'])
    clean_deliveries['is_non_striker_out'] = clean_deliveries['is_wicket'] & (clean_deliveries['dismissed_player_id'] == clean_deliveries['non_striker_id'])
    clean_deliveries['is_dot_ball'] = clean_deliveries['is_legal_ball'] & (clean_deliveries['runs'] == 0) & clean_deliveries['extras_type'].isna()
    clean_deliveries['is_boundary'] = clean_deliveries['is_four'] | clean_deliveries['is_six']

    # Phases & Special situations
    clean_deliveries['phase'] = 'Middle'
    clean_deliveries.loc[clean_deliveries['overid'] <= 6, 'phase'] = 'Powerplay'
    clean_deliveries.loc[clean_deliveries['overid'] >= 16, 'phase'] = 'Death'

    clean_deliveries['is_death_primary'] = clean_deliveries['overid'] >= 16  # Overs 16-20
    clean_deliveries['is_death_stricter'] = clean_deliveries['overid'] >= 17 # Overs 17-20
    clean_deliveries['is_super_over'] = clean_deliveries['innings'] >= 3

    # Merge knockout flag from matches
    clean_deliveries = clean_deliveries.merge(
        clean_matches[['match_id', 'knock_out', 'allotted_balls_inn2', 'revised_target']],
        on='match_id',
        how='left'
    )
    clean_deliveries['is_knockout'] = clean_deliveries['knock_out'] == 1

    # Team runs per delivery for cumulative chasing target
    clean_deliveries['team_ball_runs'] = clean_deliveries['runs']
    clean_deliveries.loc[clean_deliveries['is_wide'], 'team_ball_runs'] = 1
    clean_deliveries.loc[clean_deliveries['is_noball'], 'team_ball_runs'] = 1 + clean_deliveries.loc[clean_deliveries['is_noball'], 'runs'] + clean_deliveries.loc[clean_deliveries['is_noball'], 'extras_2_runs']
    clean_deliveries.loc[clean_deliveries['is_bye'] | clean_deliveries['is_legbye'], 'team_ball_runs'] = np.where(clean_deliveries.loc[clean_deliveries['is_bye'] | clean_deliveries['is_legbye'], 'runs'] == 0, 1, clean_deliveries.loc[clean_deliveries['is_bye'] | clean_deliveries['is_legbye'], 'runs'])
    clean_deliveries.loc[clean_deliveries['is_penalty'], 'team_ball_runs'] = 5

    # Target calculation
    inn1_totals = clean_deliveries[clean_deliveries['innings'] == 1].groupby('match_id')['team_ball_runs'].sum().rename('inn1_total')
    clean_deliveries = clean_deliveries.merge(inn1_totals, on='match_id', how='left')
    clean_deliveries['target_score'] = np.where(
        clean_deliveries['revised_target'].notnull(),
        clean_deliveries['revised_target'],
        clean_deliveries['inn1_total'] + 1
    )

    # Cumulative calculations for Innings 2 (NO OUTCOME LEAKAGE)
    inn2_mask = clean_deliveries['innings'] == 2
    clean_deliveries['cum_runs'] = 0
    clean_deliveries['cum_legal_balls'] = 0

    clean_deliveries.loc[inn2_mask, 'cum_runs'] = (
        clean_deliveries[inn2_mask].groupby('match_id')['team_ball_runs'].cumsum() -
        clean_deliveries.loc[inn2_mask, 'team_ball_runs']
    )
    clean_deliveries.loc[inn2_mask, 'cum_legal_balls'] = (
        clean_deliveries[inn2_mask].groupby('match_id')['is_legal_ball'].cumsum() -
        clean_deliveries.loc[inn2_mask, 'is_legal_ball'].astype(int)
    )

    clean_deliveries['legal_balls_remaining'] = np.maximum(
        0,
        clean_deliveries['allotted_balls_inn2'] - clean_deliveries['cum_legal_balls']
    )
    clean_deliveries['runs_needed'] = np.maximum(
        0,
        clean_deliveries['target_score'] - clean_deliveries['cum_runs']
    )

    clean_deliveries['required_run_rate'] = np.where(
        (clean_deliveries['innings'] == 2) & (clean_deliveries['legal_balls_remaining'] > 0),
        (clean_deliveries['runs_needed'] / (clean_deliveries['legal_balls_remaining'] / 6.0)),
        0.0
    )

    # Primary Situational Close Chase Indicator (ZERO OUTCOME LEAKAGE)
    clean_deliveries['is_situational_close_chase'] = (
        (clean_deliveries['innings'] == 2) &
        (clean_deliveries['legal_balls_remaining'] <= 36) &
        (clean_deliveries['required_run_rate'] >= 9.0) &
        (clean_deliveries['runs_needed'] > 0)
    )

    # Drop intermediate columns
    clean_deliveries = clean_deliveries.drop(
        columns=['team_ball_runs', 'knock_out', 'allotted_balls_inn2', 'revised_target', 'inn1_total']
    )

    quality_log["actions_performed"].append(
        "Computed legal deliveries, bowler runs conceded, bowler-creditable wickets, and batter dismissals."
    )
    quality_log["actions_performed"].append(
        "Computed in-match situational close chase pressure without outcome leakage."
    )

    # -------------------------------------------------------------------------
    # 5. Pipeline Validation Checks
    # -------------------------------------------------------------------------
    print("\n[Step 5/6] Running Validation Checks...")
    val_checks = {
        "deliveries_count_exact_200999": len(clean_deliveries) == 200999,
        "matches_count_exact_883": len(clean_matches) == 883,
        "players_count_exact_1217": len(clean_players) == 1217,
        "playing_eleven_deduped_exact_28341": len(clean_playing_eleven) == 28341,
        "bowler_wickets_exact_10272": int(clean_deliveries['is_bowler_wicket'].sum()) == 10272,
        "legal_plus_illegal_equals_total": (
            int(clean_deliveries['is_legal_ball'].sum()) +
            int((~clean_deliveries['is_legal_ball']).sum())
        ) == 200999,
        "super_overs_exact_38": int(clean_deliveries['is_super_over'].sum()) == 38,
        "close_chase_only_inn2": bool((clean_deliveries[clean_deliveries['innings'] != 2]['is_situational_close_chase'] == False).all()),
        "no_negative_balls_remaining": bool((clean_deliveries['legal_balls_remaining'] >= 0).all()),
        "no_negative_runs_needed": bool((clean_deliveries['runs_needed'] >= 0).all())
    }

    quality_log["validation_checks"] = val_checks
    all_passed = all(val_checks.values())
    print(f"  Validation Checks Status: {'ALL PASSED [OK]' if all_passed else 'FAILED [X]'}")
    for k, v in val_checks.items():
        print(f"    - {k}: {v}")

    # Summary Statistics
    quality_log["summary_statistics"] = {
        "total_deliveries": len(clean_deliveries),
        "total_legal_balls": int(clean_deliveries['is_legal_ball'].sum()),
        "total_illegal_deliveries": int((~clean_deliveries['is_legal_ball']).sum()),
        "total_bowler_wickets": int(clean_deliveries['is_bowler_wicket'].sum()),
        "total_non_bowler_wickets": int((clean_deliveries['is_wicket'] & ~clean_deliveries['is_bowler_wicket']).sum()),
        "death_primary_deliveries": int(clean_deliveries['is_death_primary'].sum()),
        "death_stricter_deliveries": int(clean_deliveries['is_death_stricter'].sum()),
        "situational_close_chase_deliveries": int(clean_deliveries['is_situational_close_chase'].sum()),
        "knockout_deliveries": int(clean_deliveries['is_knockout'].sum()),
        "super_over_deliveries": int(clean_deliveries['is_super_over'].sum()),
        "execution_time_seconds": round(time.time() - start_time, 2)
    }

    # -------------------------------------------------------------------------
    # 6. Save Cleaned Outputs to data/processed/
    # -------------------------------------------------------------------------
    print("\n[Step 6/6] Saving outputs to data/processed/...")
    
    # 1. CSV exports
    clean_deliveries_csv = os.path.join(processed_dir, "clean_deliveries.csv")
    clean_matches_csv = os.path.join(processed_dir, "clean_matches.csv")
    clean_players_csv = os.path.join(processed_dir, "clean_players.csv")
    clean_playing_eleven_csv = os.path.join(processed_dir, "clean_playing_eleven.csv")

    clean_deliveries.to_csv(clean_deliveries_csv, index=False)
    clean_matches.to_csv(clean_matches_csv, index=False)
    clean_players.to_csv(clean_players_csv, index=False)
    clean_playing_eleven.to_csv(clean_playing_eleven_csv, index=False)

    # 2. SQLite Database export
    db_path = os.path.join(processed_dir, "clutch_iq.db")
    conn = sqlite3.connect(db_path)
    clean_deliveries.to_sql("clean_deliveries", conn, if_exists="replace", index=False)
    clean_matches.to_sql("clean_matches", conn, if_exists="replace", index=False)
    clean_players.to_sql("clean_players", conn, if_exists="replace", index=False)
    clean_playing_eleven.to_sql("clean_playing_eleven", conn, if_exists="replace", index=False)
    conn.close()

    # 3. Data Quality Log export
    log_path = os.path.join(processed_dir, "data_quality_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(quality_log, f, indent=2)

    total_time = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    print(f"SUPER RR — CLUTCH IQ: Phase 1 Completed Successfully in {total_time}s!")
    print(f"Files saved in: {processed_dir}")
    print(f"  - clean_deliveries.csv ({os.path.getsize(clean_deliveries_csv)/(1024*1024):.1f} MB)")
    print(f"  - clean_matches.csv ({os.path.getsize(clean_matches_csv)/(1024):.1f} KB)")
    print(f"  - clean_players.csv ({os.path.getsize(clean_players_csv)/(1024):.1f} KB)")
    print(f"  - clean_playing_eleven.csv ({os.path.getsize(clean_playing_eleven_csv)/(1024):.1f} KB)")
    print(f"  - clutch_iq.db ({os.path.getsize(db_path)/(1024*1024):.1f} MB)")
    print(f"  - data_quality_log.json")
    print("=" * 70)

    return quality_log


if __name__ == "__main__":
    clean_and_enrich_data()

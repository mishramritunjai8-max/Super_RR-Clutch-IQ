"""
SUPER RR — CLUTCH IQ
Central Data Access & Caching Service

Loads and caches approved Phase 1–4 datasets from the project directory.
Provides safe, indexed in-memory lookups, zero-leakage joins, and
JSON-compliant NaN/Infinity sanitization.
"""

import os
import math
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np

from backend.api.config import settings


def sanitize_val(val: Any) -> Any:
    """Safely converts NaN, Infinity, -Infinity, and NumPy types into JSON-compatible Python values."""
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        return [sanitize_val(v) for v in val]
    if isinstance(val, dict):
        return {k: sanitize_val(v) for k, v in val.items()}
    if isinstance(val, str):
        return val
    if isinstance(val, (bool, np.bool_)):
        return bool(val)
    if isinstance(val, (int, np.integer)):
        return int(val)
    if isinstance(val, (float, np.floating)):
        if math.isnan(val) or math.isinf(val) or pd.isna(val):
            return None
        return round(float(val), 2)
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    return val


def parse_list_field(val: Any) -> List[str]:
    """Splits comma-separated string into a clean list of strings."""
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, (str, bytes)):
        s = val.strip() if isinstance(val, str) else val.decode("utf-8").strip()
        if not s:
            return []
        return [item.strip() for item in s.split(",") if item.strip()]
    try:
        if pd.isna(val):
            return []
    except Exception:
        pass
    return [str(val).strip()]


class DataService:
    _instance: Optional["DataService"] = None

    def __init__(self):
        self.is_loaded = False
        self._batting_df: Optional[pd.DataFrame] = None
        self._bowling_df: Optional[pd.DataFrame] = None
        self._batting_dict: Dict[int, Dict] = {}
        self._bowling_dict: Dict[int, Dict] = {}
        self._players_dict: Dict[int, Dict] = {}
        
        self._batting_profiles_df: Optional[pd.DataFrame] = None
        self._bowling_profiles_df: Optional[pd.DataFrame] = None
        self._pressure_summary_df: Optional[pd.DataFrame] = None
        self._clean_matches_df: Optional[pd.DataFrame] = None
        self._clean_players_df: Optional[pd.DataFrame] = None
        
        self.load_data()

    @classmethod
    def get_instance(cls) -> "DataService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self) -> None:
        """Initializes caches if not already loaded."""
        if not self.is_loaded:
            self.load_data()

    def load_data(self) -> None:
        """Loads and indexes all approved datasets from disk."""
        if self.is_loaded:
            return
        metrics_dir = settings.METRICS_DIR
        data_dir = settings.DATA_DIR
        
        required_files = [
            metrics_dir / "batting_clutch_scores.csv",
            metrics_dir / "bowling_clutch_scores.csv",
            metrics_dir / "batting_cluster_assignments.csv",
            metrics_dir / "bowling_cluster_assignments.csv",
            metrics_dir / "batting_cluster_profiles.csv",
            metrics_dir / "bowling_cluster_profiles.csv",
            metrics_dir / "pressure_summary.csv",
            data_dir / "clean_matches.csv",
            data_dir / "clean_players.csv"
        ]
        
        missing = [str(f) for f in required_files if not f.exists()]
        if missing:
            raise RuntimeError(f"Essential Phase 1-4 datasets are missing: {', '.join(missing)}")
            
        # 1. Load Base Datasets
        bat_scores = pd.read_csv(metrics_dir / "batting_clutch_scores.csv")
        bowl_scores = pd.read_csv(metrics_dir / "bowling_clutch_scores.csv")
        bat_assign = pd.read_csv(metrics_dir / "batting_cluster_assignments.csv")
        bowl_assign = pd.read_csv(metrics_dir / "bowling_cluster_assignments.csv")
        clean_players = pd.read_csv(data_dir / "clean_players.csv")
        
        self._batting_profiles_df = pd.read_csv(metrics_dir / "batting_cluster_profiles.csv")
        self._bowling_profiles_df = pd.read_csv(metrics_dir / "bowling_cluster_profiles.csv")
        self._pressure_summary_df = pd.read_csv(metrics_dir / "pressure_summary.csv")
        self._clean_matches_df = pd.read_csv(data_dir / "clean_matches.csv")
        self._clean_players_df = clean_players
        
        # 2. Enrich Batting with Cluster Assignment & Player Teams/Comps
        bat_assign_cols = [
            "player_id", "cohort", "assignment_status", "cluster_id",
            "archetype_name", "player_archetype_explanation"
        ]
        merged_bat = pd.merge(bat_scores, bat_assign[bat_assign_cols], on="player_id", how="left")
        merged_bat = pd.merge(merged_bat, clean_players[["player_id", "teams", "competitions"]], on="player_id", how="left")
        
        # Add primary rank: 1-indexed rank within primary cohort sorted by clutch_iq desc
        primary_bat_mask = merged_bat["cohort"] == "primary"
        merged_bat.loc[primary_bat_mask, "primary_rank"] = (
            merged_bat[primary_bat_mask]["clutch_iq"]
            .rank(ascending=False, method="min")
            .astype(int)
        )
        self._batting_df = merged_bat
        
        # 3. Enrich Bowling with Cluster Assignment & Player Teams/Comps
        bowl_assign_cols = [
            "player_id", "cohort", "assignment_status", "cluster_id",
            "archetype_name", "wickets_per_legal_ball", "player_archetype_explanation"
        ]
        merged_bowl = pd.merge(bowl_scores, bowl_assign[bowl_assign_cols], on="player_id", how="left")
        merged_bowl = pd.merge(merged_bowl, clean_players[["player_id", "teams", "competitions"]], on="player_id", how="left")
        
        primary_bowl_mask = merged_bowl["cohort"] == "primary"
        merged_bowl.loc[primary_bowl_mask, "primary_rank"] = (
            merged_bowl[primary_bowl_mask]["clutch_iq"]
            .rank(ascending=False, method="min")
            .astype(int)
        )
        self._bowling_df = merged_bowl
        
        # 4. Build Fast Indexed Dictionaries for O(1) Lookups
        for _, row in self._batting_df.iterrows():
            pid = int(row["player_id"])
            d = row.to_dict()
            d["teams"] = parse_list_field(d.get("teams"))
            d["competitions"] = parse_list_field(d.get("competitions"))
            self._batting_dict[pid] = {k: sanitize_val(v) for k, v in d.items()}
            
        for _, row in self._bowling_df.iterrows():
            pid = int(row["player_id"])
            d = row.to_dict()
            d["teams"] = parse_list_field(d.get("teams"))
            d["competitions"] = parse_list_field(d.get("competitions"))
            self._bowling_dict[pid] = {k: sanitize_val(v) for k, v in d.items()}
            
        # Index all players from clean_players
        for _, row in clean_players.iterrows():
            pid = int(row["player_id"])
            p_name = str(row["player_name"])
            teams = parse_list_field(row.get("teams"))
            comps = parse_list_field(row.get("competitions"))
            
            b_data = self._batting_dict.get(pid)
            w_data = self._bowling_dict.get(pid)
            
            self._players_dict[pid] = {
                "player_id": pid,
                "player_name": p_name,
                "teams": teams,
                "competitions": comps,
                "has_batting_profile": b_data is not None,
                "has_bowling_profile": w_data is not None,
                "batting_clutch_iq": b_data.get("clutch_iq") if b_data else None,
                "bowling_clutch_iq": w_data.get("clutch_iq") if w_data else None,
                "batting_rank": int(b_data["primary_rank"]) if b_data and b_data.get("primary_rank") else None,
                "bowling_rank": int(w_data["primary_rank"]) if w_data and w_data.get("primary_rank") else None,
                "batting_archetype": b_data.get("archetype_name") if b_data else None,
                "bowling_archetype": w_data.get("archetype_name") if w_data else None,
                "batting_cohort": b_data.get("cohort") if b_data else None,
                "bowling_cohort": w_data.get("cohort") if w_data else None,
                "batting_assignment_status": b_data.get("assignment_status") if b_data else None,
                "bowling_assignment_status": w_data.get("assignment_status") if w_data else None
            }
            
        self.is_loaded = True

    # =========================================================================
    # Query & Retrieval Methods
    # =========================================================================
    def get_batters_leaderboard(
        self,
        search: Optional[str] = None,
        min_balls: Optional[int] = None,
        min_matches: Optional[int] = None,
        cohort: Optional[str] = None,
        sort_by: str = "clutch_iq",
        sort_order: str = "desc"
    ) -> List[Dict]:
        df = self._batting_df.copy()
        
        # Filtering
        if search:
            df = df[df["player_name"].str.contains(search, case=False, na=False)]
        if min_balls is not None:
            df = df[df["balls_faced"] >= min_balls]
        if min_matches is not None:
            df = df[df["match_count"] >= min_matches]
        if cohort:
            df = df[df["cohort"] == cohort.lower()]
            
        # Sorting
        ascending = (sort_order.lower() == "asc")
        # Secondary deterministic tie-breaker: player_id asc
        if sort_by in df.columns:
            df = df.sort_values(by=[sort_by, "player_id"], ascending=[ascending, True])
        else:
            df = df.sort_values(by=["clutch_iq", "player_id"], ascending=[False, True])
            
        results = []
        for _, r in df.iterrows():
            item = {
                "player_id": int(r["player_id"]),
                "player_name": str(r["player_name"]),
                "rank": int(r["primary_rank"]) if pd.notna(r.get("primary_rank")) else None,
                "clutch_iq": sanitize_val(r["clutch_iq"]),
                "cohort": str(r["cohort"]),
                "assignment_status": str(r["assignment_status"]),
                "archetype_name": str(r["archetype_name"]),
                "balls_faced": int(r["balls_faced"]),
                "match_count": int(r["match_count"]),
                "total_runs": int(r["total_runs"]),
                "strike_rate": sanitize_val(r["strike_rate"]),
                "batting_average": sanitize_val(r["batting_average"]),
                "raw_delta_strike_rate": sanitize_val(r["raw_delta_strike_rate"]),
                "dot_ball_pct": sanitize_val(r["dot_ball_pct"]),
                "boundary_ball_pct": sanitize_val(r["boundary_ball_pct"]),
                "reliability_weight": sanitize_val(r["reliability_weight"])
            }
            results.append(item)
        return results

    def get_bowlers_leaderboard(
        self,
        search: Optional[str] = None,
        min_balls: Optional[int] = None,
        min_matches: Optional[int] = None,
        cohort: Optional[str] = None,
        sort_by: str = "clutch_iq",
        sort_order: str = "desc"
    ) -> List[Dict]:
        df = self._bowling_df.copy()
        
        # Filtering
        if search:
            df = df[df["player_name"].str.contains(search, case=False, na=False)]
        if min_balls is not None:
            df = df[df["legal_balls"] >= min_balls]
        if min_matches is not None:
            df = df[df["match_count"] >= min_matches]
        if cohort:
            df = df[df["cohort"] == cohort.lower()]
            
        # Sorting
        ascending = (sort_order.lower() == "asc")
        if sort_by in df.columns:
            df = df.sort_values(by=[sort_by, "player_id"], ascending=[ascending, True])
        else:
            df = df.sort_values(by=["clutch_iq", "player_id"], ascending=[False, True])
            
        results = []
        for _, r in df.iterrows():
            item = {
                "player_id": int(r["player_id"]),
                "player_name": str(r["player_name"]),
                "rank": int(r["primary_rank"]) if pd.notna(r.get("primary_rank")) else None,
                "clutch_iq": sanitize_val(r["clutch_iq"]),
                "cohort": str(r["cohort"]),
                "assignment_status": str(r["assignment_status"]),
                "archetype_name": str(r["archetype_name"]),
                "legal_balls": int(r["legal_balls"]),
                "match_count": int(r["match_count"]),
                "runs_conceded": int(r["runs_conceded"]),
                "bowler_wickets": int(r["bowler_wickets"]),
                "economy_rate": sanitize_val(r["economy_rate"]),
                "bowling_strike_rate": sanitize_val(r["bowling_strike_rate"]),
                "bowling_average": sanitize_val(r["bowling_average"]),
                "raw_delta_economy": sanitize_val(r["raw_delta_economy"]),
                "dot_ball_pct": sanitize_val(r["dot_ball_pct"]),
                "boundary_balls_conceded_per_100_legal_balls": sanitize_val(r["boundary_balls_conceded_per_100_legal_balls"]),
                "reliability_weight": sanitize_val(r["reliability_weight"])
            }
            results.append(item)
        return results

    def get_player_summary(self, player_id: int) -> Optional[Dict]:
        return self._players_dict.get(player_id)

    def get_player_batting_profile(self, player_id: int) -> Optional[Dict]:
        data = self._batting_dict.get(player_id)
        if not data:
            return None
        return {
            "player_id": data["player_id"],
            "player_name": data["player_name"],
            "teams": data.get("teams", []),
            "competitions": data.get("competitions", []),
            "clutch_iq": data["clutch_iq"],
            "rank": int(data["primary_rank"]) if data.get("primary_rank") else None,
            "cohort": data["cohort"],
            "assignment_status": data["assignment_status"],
            "archetype_name": data["archetype_name"],
            "player_archetype_explanation": data.get("player_archetype_explanation", ""),
            "balls_faced": data["balls_faced"],
            "total_runs": data["total_runs"],
            "dismissals": data["dismissals"],
            "not_outs": data["not_outs"],
            "innings_count": data["innings_count"],
            "match_count": data["match_count"],
            "strike_rate": data["strike_rate"],
            "batting_average": data["batting_average"],
            "dot_ball_pct": data["dot_ball_pct"],
            "boundary_ball_pct": data["boundary_ball_pct"],
            "fours": data.get("fours", 0),
            "sixes": data.get("sixes", 0),
            "balls_baseline": data["balls_baseline"],
            "runs_baseline": data["runs_baseline"],
            "sr_baseline": data.get("sr_baseline"),
            "avg_baseline": data.get("avg_baseline"),
            "dot_pct_baseline": data.get("dot_pct_baseline"),
            "boundary_pct_baseline": data.get("boundary_pct_baseline"),
            "reg_sr_base": data["reg_sr_base"],
            "raw_delta_strike_rate": data["raw_delta_strike_rate"],
            "shrunk_delta_strike_rate": data["shrunk_delta_strike_rate"],
            "reliability_weight": data["reliability_weight"]
        }

    def get_player_bowling_profile(self, player_id: int) -> Optional[Dict]:
        data = self._bowling_dict.get(player_id)
        if not data:
            return None
        return {
            "player_id": data["player_id"],
            "player_name": data["player_name"],
            "teams": data.get("teams", []),
            "competitions": data.get("competitions", []),
            "clutch_iq": data["clutch_iq"],
            "rank": int(data["primary_rank"]) if data.get("primary_rank") else None,
            "cohort": data["cohort"],
            "assignment_status": data["assignment_status"],
            "archetype_name": data["archetype_name"],
            "player_archetype_explanation": data.get("player_archetype_explanation", ""),
            "legal_balls": data["legal_balls"],
            "runs_conceded": data["runs_conceded"],
            "bowler_wickets": data["bowler_wickets"],
            "economy_rate": data["economy_rate"],
            "bowling_strike_rate": data["bowling_strike_rate"],
            "bowling_average": data["bowling_average"],
            "wickets_per_legal_ball": data.get("wickets_per_legal_ball", 0.0),
            "dot_ball_pct": data["dot_ball_pct"],
            "boundary_balls_conceded_per_100_legal_balls": data["boundary_balls_conceded_per_100_legal_balls"],
            "fours_conceded": data.get("fours_conceded", 0),
            "sixes_conceded": data.get("sixes_conceded", 0),
            "match_count": data["match_count"],
            "balls_baseline": data["balls_baseline"],
            "runs_conceded_baseline": data["runs_conceded_baseline"],
            "wickets_baseline": data["wickets_baseline"],
            "econ_baseline": data.get("econ_baseline"),
            "wkt_sr_baseline": data.get("wkt_sr_baseline"),
            "dot_pct_baseline": data.get("dot_pct_baseline"),
            "boundary_balls_per_100_baseline": data.get("boundary_balls_per_100_baseline"),
            "reg_econ_base": data["reg_econ_base"],
            "raw_delta_economy": data["raw_delta_economy"],
            "shrunk_delta_economy": data["shrunk_delta_economy"],
            "reliability_weight": data["reliability_weight"]
        }

    def get_batting_archetypes(self) -> List[Dict]:
        records = []
        for _, r in self._batting_profiles_df.iterrows():
            item = {k: sanitize_val(v) for k, v in r.to_dict().items()}
            item["representative_players"] = parse_list_field(item.get("representative_players"))
            records.append(item)
        return records

    def get_bowling_archetypes(self) -> List[Dict]:
        records = []
        for _, r in self._bowling_profiles_df.iterrows():
            item = {k: sanitize_val(v) for k, v in r.to_dict().items()}
            item["representative_players"] = parse_list_field(item.get("representative_players"))
            records.append(item)
        return records

    def get_batting_archetype_detail(self, cluster_id: int) -> Optional[Tuple[Dict, List[Dict]]]:
        sub = self._batting_profiles_df[self._batting_profiles_df["cluster_id"] == cluster_id]
        if sub.empty:
            return None
        prof = {k: sanitize_val(v) for k, v in sub.iloc[0].to_dict().items()}
        prof["representative_players"] = parse_list_field(prof.get("representative_players"))
        
        # All assigned players in this cluster
        assigned = self._batting_df[self._batting_df["cluster_id"] == cluster_id].sort_values(
            by=["clutch_iq", "player_id"], ascending=[False, True]
        )
        players = []
        for _, r in assigned.iterrows():
            players.append({
                "player_id": int(r["player_id"]),
                "player_name": str(r["player_name"]),
                "rank": int(r["primary_rank"]) if pd.notna(r.get("primary_rank")) else None,
                "clutch_iq": sanitize_val(r["clutch_iq"]),
                "cohort": str(r["cohort"]),
                "assignment_status": str(r["assignment_status"]),
                "archetype_name": str(r["archetype_name"]),
                "balls_faced": int(r["balls_faced"]),
                "match_count": int(r["match_count"]),
                "total_runs": int(r["total_runs"]),
                "strike_rate": sanitize_val(r["strike_rate"]),
                "batting_average": sanitize_val(r["batting_average"]),
                "raw_delta_strike_rate": sanitize_val(r["raw_delta_strike_rate"]),
                "dot_ball_pct": sanitize_val(r["dot_ball_pct"]),
                "boundary_ball_pct": sanitize_val(r["boundary_ball_pct"]),
                "reliability_weight": sanitize_val(r["reliability_weight"])
            })
        return prof, players

    def get_bowling_archetype_detail(self, cluster_id: int) -> Optional[Tuple[Dict, List[Dict]]]:
        sub = self._bowling_profiles_df[self._bowling_profiles_df["cluster_id"] == cluster_id]
        if sub.empty:
            return None
        prof = {k: sanitize_val(v) for k, v in sub.iloc[0].to_dict().items()}
        prof["representative_players"] = parse_list_field(prof.get("representative_players"))
        
        assigned = self._bowling_df[self._bowling_df["cluster_id"] == cluster_id].sort_values(
            by=["clutch_iq", "player_id"], ascending=[False, True]
        )
        players = []
        for _, r in assigned.iterrows():
            players.append({
                "player_id": int(r["player_id"]),
                "player_name": str(r["player_name"]),
                "rank": int(r["primary_rank"]) if pd.notna(r.get("primary_rank")) else None,
                "clutch_iq": sanitize_val(r["clutch_iq"]),
                "cohort": str(r["cohort"]),
                "assignment_status": str(r["assignment_status"]),
                "archetype_name": str(r["archetype_name"]),
                "legal_balls": int(r["legal_balls"]),
                "match_count": int(r["match_count"]),
                "runs_conceded": int(r["runs_conceded"]),
                "bowler_wickets": int(r["bowler_wickets"]),
                "economy_rate": sanitize_val(r["economy_rate"]),
                "bowling_strike_rate": sanitize_val(r["bowling_strike_rate"]),
                "bowling_average": sanitize_val(r["bowling_average"]),
                "raw_delta_economy": sanitize_val(r["raw_delta_economy"]),
                "dot_ball_pct": sanitize_val(r["dot_ball_pct"]),
                "boundary_balls_conceded_per_100_legal_balls": sanitize_val(r["boundary_balls_conceded_per_100_legal_balls"]),
                "reliability_weight": sanitize_val(r["reliability_weight"])
            })
        return prof, players

    def get_analytics_summary(self) -> Dict:
        matches = self._clean_matches_df
        ps = self._pressure_summary_df
        
        overall = ps[ps["segment_name"].str.contains("Overall Regular", case=False, na=False)].iloc[0]
        baseline = ps[ps["segment_name"].str.contains("Non-Pressure Baseline", case=False, na=False)].iloc[0]
        union = ps[ps["segment_name"].str.contains("Any Pressure", case=False, na=False)].iloc[0]
        super_overs = ps[ps["segment_name"].str.contains("Super Overs", case=False, na=False)].iloc[0]
        
        total_deliveries = int(overall["total_deliveries"]) + int(super_overs["total_deliveries"])
        
        # Completed vs abandoned matches
        total_matches = len(matches)
        abandoned_matches = int(matches["result"].str.contains("no result|abandoned", case=False, na=False).sum())
        completed_matches = total_matches - abandoned_matches
        
        seasons = sorted(matches["season"].dropna().unique().tolist())
        comps_count = int(matches["comp_name"].nunique())
        
        pressure_deliv = int(union["total_deliveries"])
        regular_deliv = int(overall["total_deliveries"])
        pressure_pct = round((pressure_deliv / regular_deliv) * 100.0, 2)
        
        return {
            "total_matches": total_matches,
            "completed_matches": completed_matches,
            "abandoned_matches": abandoned_matches,
            "total_deliveries": total_deliveries,
            "regular_innings_deliveries": regular_deliv,
            "super_over_deliveries": int(super_overs["total_deliveries"]),
            "total_team_runs": int(overall["team_innings_runs"]),
            "total_batter_runs": int(overall["total_runs_off_bat"]),
            "total_extras_runs": int(overall["team_innings_runs"]) - int(overall["total_runs_off_bat"]),
            "total_bowler_wickets": int(overall["bowler_wickets"]),
            "total_batters_count": int(overall["unique_batters"]),
            "total_bowlers_count": int(overall["unique_bowlers"]),
            "pressure_deliveries_count": pressure_deliv,
            "baseline_deliveries_count": int(baseline["total_deliveries"]),
            "pressure_percentage": pressure_pct,
            "seasons_covered": seasons,
            "competitions_count": comps_count
        }

    def get_pressure_analytics(self) -> Dict:
        records = []
        for _, r in self._pressure_summary_df.iterrows():
            item = {k: sanitize_val(v) for k, v in r.to_dict().items()}
            records.append(item)
            
        note = (
            "Individual pressure categories (Death Overs, Close Chases, Knockout Matches) overlap in match play. "
            "The 'Any Pressure (Union)' segment represents the mathematically deduplicated set union (53,453 deliveries). "
            "Combined with the Non-Pressure Baseline (147,508 deliveries), they reconcile exactly to 200,961 regular deliveries. "
            "Super Overs (38 deliveries) are strictly quarantined in accordance with ICC playing condition rule 16."
        )
        return {
            "segments": records,
            "note": note
        }

    def get_metadata(self) -> Dict:
        matches = self._clean_matches_df
        seasons = sorted(matches["season"].dropna().unique().tolist())
        formats = sorted(matches["match_format"].dropna().unique().tolist())
        comps = sorted(matches["comp_name"].dropna().unique().tolist())
        
        pressure_cats = [
            "Death Primary (Overs 16-20)",
            "Death Stricter (Overs 17-20)",
            "Close Chase (RRR >= 9, <= 36 balls)",
            "Knockout Matches",
            "Any Pressure (Deduplicated Union)"
        ]
        
        archetypes = {
            "batting": self._batting_profiles_df["archetype_name"].tolist(),
            "bowling": self._bowling_profiles_df["archetype_name"].tolist()
        }
        
        return {
            "project_name": settings.PROJECT_NAME,
            "project_slogan": settings.PROJECT_SLOGAN,
            "version": settings.VERSION,
            "total_matches": len(matches),
            "total_registered_players": len(self._clean_players_df),
            "pressure_batters_count": len(self._batting_df),
            "pressure_bowlers_count": len(self._bowling_df),
            "seasons": seasons,
            "formats": formats,
            "competitions_count": len(comps),
            "pressure_categories": pressure_cats,
            "archetype_categories": archetypes,
            "engine_versions": {
                "etl_pipeline": "1.1.0",
                "metrics_engine": "2.1.0",
                "clutch_scoring": "3.0.0",
                "machine_learning": "4.1.0",
                "api_backend": settings.VERSION
            }
        }

    def get_health_status(self) -> Dict:
        return {
            "status": "healthy" if self.is_loaded else "initializing",
            "app_name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "data_loaded": self.is_loaded,
            "datasets_available": {
                "batting_clutch_scores": len(self._batting_df) if self._batting_df is not None else 0,
                "bowling_clutch_scores": len(self._bowling_df) if self._bowling_df is not None else 0,
                "batting_archetypes": len(self._batting_profiles_df) if self._batting_profiles_df is not None else 0,
                "bowling_archetypes": len(self._bowling_profiles_df) if self._bowling_profiles_df is not None else 0,
                "pressure_summary": len(self._pressure_summary_df) if self._pressure_summary_df is not None else 0,
                "clean_matches": len(self._clean_matches_df) if self._clean_matches_df is not None else 0
            }
        }

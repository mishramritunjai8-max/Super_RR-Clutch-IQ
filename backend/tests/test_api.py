"""
SUPER RR — CLUTCH IQ
Phase 5: FastAPI REST API Automated Test Suite
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.api.services.data_service import DataService


@pytest.fixture(scope="module")
def client():
    """Initializes and provides the TestClient instance."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def data_service():
    """Provides direct access to loaded DataService for fixture assertions."""
    service = DataService.get_instance()
    service.initialize()
    return service


# =====================================================================
# 1. System, Health & Metadata Tests
# =====================================================================
class TestHealthAndMetadata:
    def test_root_endpoint_returns_welcome_and_docs(self, client: TestClient):
        res = client.get("/")
        assert res.status_code == 200
        data = res.json()
        assert "SUPER RR" in data["project"]
        assert data["docs_url"] == "/docs"
        assert data["api_v1_base"] == "/api/v1"

    def test_top_level_health_probe(self, client: TestClient):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["data_loaded"] is True
        assert data["datasets_available"]["batting_clutch_scores"] == 775
        assert data["datasets_available"]["bowling_clutch_scores"] == 543

    def test_api_v1_health_probe(self, client: TestClient):
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["data_loaded"] is True

    def test_metadata_counts_and_versions(self, client: TestClient):
        res = client.get("/api/v1/metadata")
        assert res.status_code == 200
        data = res.json()
        assert data["total_registered_players"] == 1217
        assert data["pressure_batters_count"] == 775
        assert data["pressure_bowlers_count"] == 543
        assert data["total_matches"] == 883
        assert len(data["pressure_categories"]) == 5
        assert len(data["archetype_categories"]["batting"]) == 3
        assert len(data["archetype_categories"]["bowling"]) == 3
        assert data["engine_versions"]["api_backend"] == "1.0.0"


# =====================================================================
# 2. Batting Leaderboard Tests
# =====================================================================
class TestBattersLeaderboard:
    def test_batters_leaderboard_default_pagination(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/batters")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data and "pagination" in data
        assert len(data["items"]) == 20
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 20
        assert data["pagination"]["total_records"] == 249  # primary default
        assert data["pagination"]["has_next"] is True
        assert data["pagination"]["has_prev"] is False

    def test_batters_leaderboard_custom_page_size(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/batters?page=2&page_size=10")
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) == 10
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["page_size"] == 10
        assert data["pagination"]["has_prev"] is True

    def test_batters_leaderboard_cohort_filtering(self, client: TestClient):
        # Emerging cohort
        res_emerging = client.get("/api/v1/leaderboards/batters?cohort=emerging")
        assert res_emerging.status_code == 200
        data_emerging = res_emerging.json()
        assert data_emerging["pagination"]["total_records"] == 526
        for item in data_emerging["items"]:
            assert item["cohort"] == "emerging"
            assert item["rank"] is None

        # All cohorts
        res_all = client.get("/api/v1/leaderboards/batters?cohort=all")
        assert res_all.status_code == 200
        data_all = res_all.json()
        assert data_all["pagination"]["total_records"] == 775

    def test_batters_leaderboard_search_filter(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/batters?search=Najibullah")
        assert res.status_code == 200
        data = res.json()
        assert data["pagination"]["total_records"] >= 1
        assert any("Najibullah" in item["player_name"] for item in data["items"])

    def test_batters_leaderboard_sorting_ascending_and_descending(self, client: TestClient):
        res_desc = client.get("/api/v1/leaderboards/batters?sort_by=clutch_iq&sort_order=desc")
        assert res_desc.status_code == 200
        items_desc = res_desc.json()["items"]
        assert items_desc[0]["clutch_iq"] >= items_desc[1]["clutch_iq"]

        res_asc = client.get("/api/v1/leaderboards/batters?sort_by=clutch_iq&sort_order=asc")
        assert res_asc.status_code == 200
        items_asc = res_asc.json()["items"]
        assert items_asc[0]["clutch_iq"] <= items_asc[1]["clutch_iq"]

    def test_batters_leaderboard_invalid_sort_field_returns_400(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/batters?sort_by=invalid_field")
        assert res.status_code == 400
        assert "Invalid sort_by field" in res.json()["detail"]

    def test_batters_leaderboard_min_balls_filter(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/batters?min_balls=150")
        assert res.status_code == 200
        data = res.json()
        for item in data["items"]:
            assert item["balls_faced"] >= 150

    def test_batters_leaderboard_top_10_consistency(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/batters?page_size=10&cohort=primary")
        assert res.status_code == 200
        items = res.json()["items"]
        assert items[0]["player_name"] == "Najibullah Zadran"
        assert items[0]["rank"] == 1
        assert pytest.approx(items[0]["clutch_iq"], 0.1) == 96.59


# =====================================================================
# 3. Bowling Leaderboard Tests
# =====================================================================
class TestBowlersLeaderboard:
    def test_bowlers_leaderboard_default_pagination(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/bowlers")
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) == 20
        assert data["pagination"]["total_records"] == 219  # primary default

    def test_bowlers_leaderboard_custom_page_size(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/bowlers?page=1&page_size=5")
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) == 5
        assert data["pagination"]["page_size"] == 5

    def test_bowlers_leaderboard_cohort_filtering(self, client: TestClient):
        res_emerging = client.get("/api/v1/leaderboards/bowlers?cohort=emerging")
        assert res_emerging.status_code == 200
        data_emerging = res_emerging.json()
        assert data_emerging["pagination"]["total_records"] == 324
        for item in data_emerging["items"]:
            assert item["cohort"] == "emerging"

        res_all = client.get("/api/v1/leaderboards/bowlers?cohort=all")
        assert res_all.status_code == 200
        data_all = res_all.json()
        assert data_all["pagination"]["total_records"] == 543

    def test_bowlers_leaderboard_search_filter(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/bowlers?search=Rasikh")
        assert res.status_code == 200
        data = res.json()
        assert data["pagination"]["total_records"] >= 1
        assert any("Rasikh" in item["player_name"] for item in data["items"])

    def test_bowlers_leaderboard_sorting(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/bowlers?sort_by=economy_rate&sort_order=asc")
        assert res.status_code == 200
        items = res.json()["items"]
        assert items[0]["economy_rate"] <= items[1]["economy_rate"]

    def test_bowlers_leaderboard_invalid_sort_returns_400(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/bowlers?sort_by=non_existent_field")
        assert res.status_code == 400
        assert "Invalid sort_by field" in res.json()["detail"]

    def test_bowlers_leaderboard_top_10_consistency(self, client: TestClient):
        res = client.get("/api/v1/leaderboards/bowlers?page_size=10&cohort=primary")
        assert res.status_code == 200
        items = res.json()["items"]
        assert items[0]["player_name"] == "Rasikh Salam"
        assert items[0]["rank"] == 1
        assert pytest.approx(items[0]["clutch_iq"], 0.1) == 76.84


# =====================================================================
# 4. Player Profile & Role Boundary Tests
# =====================================================================
class TestPlayerProfiles:
    def test_player_detail_valid_all_rounder(self, client: TestClient):
        # Piyush Chawla (player_id: 23) has both batting and bowling
        res = client.get("/api/v1/players/23")
        assert res.status_code == 200
        data = res.json()
        assert data["player_id"] == 23
        assert data["has_batting_profile"] is True
        assert data["has_bowling_profile"] is True
        assert data["batting_clutch_iq"] is not None
        assert data["bowling_clutch_iq"] is not None

    def test_player_detail_batting_only(self, client: TestClient):
        # Najibullah Zadran (player_id: 2533)
        res = client.get("/api/v1/players/2533")
        assert res.status_code == 200
        data = res.json()
        assert data["player_id"] == 2533
        assert data["has_batting_profile"] is True
        assert data["has_bowling_profile"] is False
        assert data["bowling_clutch_iq"] is None

    def test_player_detail_bowling_only(self, client: TestClient):
        # Varun Aaron (player_id: 1028)
        res = client.get("/api/v1/players/1028")
        assert res.status_code == 200
        data = res.json()
        assert data["player_id"] == 1028
        assert data["has_batting_profile"] is False
        assert data["has_bowling_profile"] is True
        assert data["batting_clutch_iq"] is None

    def test_player_detail_nonexistent_returns_404(self, client: TestClient):
        res = client.get("/api/v1/players/999999")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_player_batting_profile_valid(self, client: TestClient):
        res = client.get("/api/v1/players/2533/batting")
        assert res.status_code == 200
        data = res.json()
        assert data["player_id"] == 2533
        assert data["player_name"] == "Najibullah Zadran"
        assert data["strike_rate"] > 100.0
        assert "archetype_name" in data

    def test_player_batting_profile_for_bowling_only_returns_404(self, client: TestClient):
        # Varun Aaron has no batting profile
        res = client.get("/api/v1/players/1028/batting")
        assert res.status_code == 404
        assert "no pressure batting profile" in res.json()["detail"].lower()

    def test_player_bowling_profile_valid(self, client: TestClient):
        res = client.get("/api/v1/players/7327/bowling")
        assert res.status_code == 200
        data = res.json()
        assert data["player_id"] == 7327
        assert data["player_name"] == "Rasikh Salam"
        assert data["economy_rate"] > 0.0

    def test_player_bowling_profile_for_batting_only_returns_404(self, client: TestClient):
        # Najibullah Zadran has no bowling profile
        res = client.get("/api/v1/players/2533/bowling")
        assert res.status_code == 404
        assert "no pressure bowling profile" in res.json()["detail"].lower()


# =====================================================================
# 5. Player Comparison Tests
# =====================================================================
class TestPlayerComparison:
    def test_compare_two_valid_players(self, client: TestClient):
        res = client.get("/api/v1/players/compare?player_ids=2533,7327")
        assert res.status_code == 200
        data = res.json()
        assert len(data["players"]) == 2
        pids = [p["player_id"] for p in data["players"]]
        assert 2533 in pids and 7327 in pids

    def test_compare_five_players_max(self, client: TestClient):
        res = client.get("/api/v1/players/compare?player_ids=2533,7327,23,47,8")
        assert res.status_code == 200
        data = res.json()
        assert len(data["players"]) == 5

    def test_compare_single_player_returns_400(self, client: TestClient):
        res = client.get("/api/v1/players/compare?player_ids=2533")
        assert res.status_code == 400
        assert "at least 2 distinct player ids" in res.json()["detail"].lower()

    def test_compare_exceeding_max_players_returns_400(self, client: TestClient):
        res = client.get("/api/v1/players/compare?player_ids=1,2,3,4,5,6")
        assert res.status_code == 400
        assert "maximum of 5 players" in res.json()["detail"].lower()

    def test_compare_nonexistent_player_returns_404(self, client: TestClient):
        res = client.get("/api/v1/players/compare?player_ids=2533,999999")
        assert res.status_code == 404
        assert "999999" in res.json()["detail"]

    def test_compare_duplicate_ids_handles_cleanly(self, client: TestClient):
        # Duplicate IDs collapse to 1 unique ID, triggering 400
        res = client.get("/api/v1/players/compare?player_ids=2533,2533")
        assert res.status_code == 400
        assert "at least 2 distinct player ids" in res.json()["detail"].lower()


# =====================================================================
# 6. Archetypes Endpoints Tests
# =====================================================================
class TestArchetypes:
    def test_get_batting_archetypes_list(self, client: TestClient):
        res = client.get("/api/v1/archetypes/batting")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 3
        cluster_ids = [c["cluster_id"] for c in data]
        assert set(cluster_ids) == {0, 1, 2}
        total_players = sum(c["total_player_count"] for c in data)
        assert total_players == 775

    def test_get_bowling_archetypes_list(self, client: TestClient):
        res = client.get("/api/v1/archetypes/bowling")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 3
        cluster_ids = [c["cluster_id"] for c in data]
        assert set(cluster_ids) == {0, 1, 2}
        total_players = sum(c["total_player_count"] for c in data)
        assert total_players == 543

    def test_get_batting_archetype_detail_valid(self, client: TestClient):
        for cid in [0, 1, 2]:
            res = client.get(f"/api/v1/archetypes/batting/{cid}?page_size=5")
            assert res.status_code == 200
            data = res.json()
            assert data["profile"]["cluster_id"] == cid
            assert len(data["players"]["items"]) == 5
            assert data["players"]["pagination"]["total_records"] == data["profile"]["total_player_count"]

    def test_get_batting_archetype_detail_invalid_cluster_404(self, client: TestClient):
        res = client.get("/api/v1/archetypes/batting/99")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_get_bowling_archetype_detail_valid(self, client: TestClient):
        for cid in [0, 1, 2]:
            res = client.get(f"/api/v1/archetypes/bowling/{cid}?page_size=5")
            assert res.status_code == 200
            data = res.json()
            assert data["profile"]["cluster_id"] == cid
            assert len(data["players"]["items"]) == 5

    def test_get_bowling_archetype_detail_invalid_cluster_404(self, client: TestClient):
        res = client.get("/api/v1/archetypes/bowling/99")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_archetype_cohort_split_consistency(self, client: TestClient):
        res = client.get("/api/v1/archetypes/batting")
        assert res.status_code == 200
        for item in res.json():
            assert item["primary_player_count"] + item["emerging_player_count"] == item["total_player_count"]


# =====================================================================
# 7. Macro Analytics & Pressure Segments Tests
# =====================================================================
class TestAnalyticsAndPressure:
    def test_analytics_summary_macro_totals(self, client: TestClient):
        res = client.get("/api/v1/analytics/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_deliveries"] == 200999
        assert data["regular_innings_deliveries"] == 200961
        assert data["super_over_deliveries"] == 38
        assert data["total_team_runs"] == 281418
        assert data["total_batter_runs"] == 269506
        assert data["total_extras_runs"] == 11912
        assert data["total_bowler_wickets"] == 10261
        assert data["total_batters_count"] == 888
        assert data["total_bowlers_count"] == 647
        assert data["pressure_deliveries_count"] == 53453
        assert data["baseline_deliveries_count"] == 147508

    def test_analytics_summary_matches_counts(self, client: TestClient):
        res = client.get("/api/v1/analytics/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_matches"] == 883
        assert data["completed_matches"] == 843
        assert data["abandoned_matches"] == 40
        assert data["completed_matches"] + data["abandoned_matches"] == data["total_matches"]

    def test_pressure_analytics_segments_count(self, client: TestClient):
        res = client.get("/api/v1/analytics/pressure")
        assert res.status_code == 200
        data = res.json()
        assert len(data["segments"]) == 8
        assert "deduplicated" in data["note"].lower()

    def test_pressure_analytics_union_baseline_reconciliation(self, client: TestClient):
        res = client.get("/api/v1/analytics/pressure")
        assert res.status_code == 200
        segments = {s["segment_name"]: s for s in res.json()["segments"]}
        
        # Verify exact delivery reconciliation
        regular = segments["Overall Regular (Innings 1-2)"]["total_deliveries"]
        baseline = segments["Non-Pressure Baseline"]["total_deliveries"]
        union = segments["Any Pressure (Union)"]["total_deliveries"]
        assert regular == 200961
        assert baseline == 147508
        assert union == 53453
        assert baseline + union == regular

    def test_pressure_analytics_super_overs_isolation(self, client: TestClient):
        res = client.get("/api/v1/analytics/pressure")
        assert res.status_code == 200
        segments = {s["segment_name"]: s for s in res.json()["segments"]}
        super_overs = segments["Super Overs (Innings >= 3)"]
        assert super_overs["total_deliveries"] == 38


# =====================================================================
# 8. Reliability, Performance & Security Tests
# =====================================================================
class TestReliabilityAndSecurity:
    def test_no_nan_or_inf_in_json_responses(self, client: TestClient):
        endpoints = [
            "/api/v1/health",
            "/api/v1/metadata",
            "/api/v1/leaderboards/batters?page_size=50",
            "/api/v1/leaderboards/bowlers?page_size=50",
            "/api/v1/players/23",
            "/api/v1/archetypes/batting",
            "/api/v1/archetypes/bowling",
            "/api/v1/analytics/summary",
            "/api/v1/analytics/pressure"
        ]
        for ep in endpoints:
            res = client.get(ep)
            assert res.status_code == 200, f"Endpoint {ep} failed: {res.text}"
            text = res.text
            assert "NaN" not in text, f"NaN found in {ep} response"
            assert "Infinity" not in text, f"Infinity found in {ep} response"
            assert "-Infinity" not in text, f"-Infinity found in {ep} response"

    def test_process_time_header_present(self, client: TestClient):
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        assert "X-Process-Time-Ms" in res.headers
        val = float(res.headers["X-Process-Time-Ms"])
        assert val >= 0.0

    def test_validation_error_returns_standard_error_schema(self, client: TestClient):
        # Trigger validation error by passing invalid parameter type (string for int)
        res = client.get("/api/v1/leaderboards/batters?page=not_a_number")
        assert res.status_code == 422
        data = res.json()
        assert "detail" in data
        assert data["status_code"] == 422
        assert "timestamp" in data

    def test_not_found_returns_standard_error_schema(self, client: TestClient):
        res = client.get("/api/v1/non_existent_route")
        assert res.status_code == 404
        data = res.json()
        assert "detail" in data
        assert data["status_code"] == 404
        assert "timestamp" in data

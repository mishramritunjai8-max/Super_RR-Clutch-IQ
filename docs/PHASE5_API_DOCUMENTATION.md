# SUPER RR — CLUTCH IQ: Phase 5 API Documentation

**Project**: SUPER RR — CLUTCH IQ: Beyond Statistics  
**Subtitle**: Discovering Players Who Perform Under Pressure (Rajasthan Royals Hackathon)  
**API Version**: `1.0.0`  
**Base URL**: `/api/v1`  
**Documentation Endpoints**: Interactive Swagger UI at `http://localhost:8000/docs`, ReDoc at `http://localhost:8000/redoc`, OpenAPI JSON schema at `http://localhost:8000/openapi.json`.

---

## 1. Overview & Architecture

The **CLUTCH IQ Backend API** is an asynchronous, high-performance RESTful API built on **FastAPI**, **Pydantic v2**, and **Starlette**. It exposes approved empirical cricket analytics, Bayesian credibility-shrunk Clutch IQ rankings, and unsupervised K-Means player archetypes directly from in-memory indexed datasets.

### Key Architectural Characteristics
- **Zero-Database Design**: Powered exclusively by verified CSV datasets and scikit-learn models generated across Phases 1–4.
- **In-Memory Caching & $O(1)$ Hash Lookups**: All player records, cluster assignments, and leaderboards are pre-indexed on application startup during the lifespan context manager.
- **Sub-50ms Latency Guarantee**: Direct hash lookups and memory-mapped dataframe operations ensure individual player profiles and comparison queries execute in 2–4 milliseconds, and complex filtered leaderboards in 25–35 milliseconds.
- **Strict Data Sanitization**: Guaranteed zero `NaN`, `Infinity`, or `-Infinity` tokens in any JSON response. All invalid floating-point values are cleanly converted to `null` or rounded to 2 decimal places.
- **Observability**: Every HTTP response includes an `X-Process-Time-Ms` telemetry header measuring end-to-end server execution time.

---

## 2. Server Execution Instructions

To start the local development server:

```powershell
# From the project root (c:\Users\Lenovo\OneDrive\Desktop\SuperRR-Clutch-IQ)
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Variables
- `ENVIRONMENT`: Deployment environment (`development` [default], `staging`, `production`).
- `CORS_ORIGINS`: Comma-separated list of allowed origins (defaults to `http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,*`).

---

## 3. Global Headers & Error Format

### Telemetry Header
Every HTTP response contains:
```http
X-Process-Time-Ms: 2.15
```

### Standard Error Response Schema
All error responses (HTTP 400, 404, 422, 500) follow a unified JSON envelope:

```json
{
  "detail": "Descriptive error message explaining the failure condition",
  "status_code": 404,
  "timestamp": "2026-11-13T22:15:30.123456+00:00"
}
```

---

## 4. Complete Endpoint Reference

### 4.1 System & Health

#### `GET /health`
Top-level container and orchestrator probe.
- **Response**: `200 OK`
```json
{
  "status": "healthy",
  "app_name": "SUPER RR — CLUTCH IQ: Beyond Statistics",
  "version": "1.0.0",
  "environment": "development",
  "data_loaded": true,
  "datasets_available": {
    "batting_clutch_scores": 775,
    "bowling_clutch_scores": 543,
    "batting_archetypes": 3,
    "bowling_archetypes": 3,
    "pressure_summary": 8,
    "clean_matches": 883
  }
}
```

#### `GET /api/v1/health`
Standard API v1 health check endpoint.
- **Response**: `200 OK` (Same schema as top-level probe).

#### `GET /api/v1/metadata`
Provides comprehensive system constants, tournament boundaries, season lists, and model pipeline versions.
- **Response**: `200 OK`
```json
{
  "project_name": "SUPER RR — CLUTCH IQ: Beyond Statistics",
  "project_slogan": "Discovering Players Who Perform Under Pressure",
  "version": "1.0.0",
  "total_matches": 883,
  "total_registered_players": 1217,
  "pressure_batters_count": 775,
  "pressure_bowlers_count": 543,
  "seasons": ["2021/22", "2022", "2022/23", "2023", "2024"],
  "formats": ["T20"],
  "competitions_count": 14,
  "pressure_categories": [
    "Death Primary (Overs 16-20)",
    "Death Stricter (Overs 17-20)",
    "Close Chase (RRR >= 9, <= 36 balls)",
    "Knockout Matches",
    "Any Pressure (Deduplicated Union)"
  ],
  "archetype_categories": {
    "batting": [
      "Pressure-Struggling / Low-Tempo Batters",
      "Anchor Accumulators & Stabilizers Under Pressure",
      "Explosive Pressure Finishers & Boundary Hitters"
    ],
    "bowling": [
      "Pressure-Vulnerable / High-Concession Bowlers",
      "Economical Pressure Controllers",
      "Moderate-Containment / Mid-Tier Pressure Bowlers"
    ]
  },
  "engine_versions": {
    "etl_pipeline": "1.1.0",
    "metrics_engine": "2.1.0",
    "clutch_scoring": "3.0.0",
    "machine_learning": "4.1.0",
    "api_backend": "1.0.0"
  }
}
```

---

### 4.2 Leaderboards

#### `GET /api/v1/leaderboards/batters`
Returns a paginated list of batters ranked by Clutch IQ.
- **Query Parameters**:
  - `page` (`int`, default `1`, min `1`): Page number (1-indexed).
  - `page_size` (`int`, default `20`, min `1`, max `100`): Items per page.
  - `cohort` (`str`, default `"primary"`): Filter by cohort: `"primary"` ($\ge 50$ balls, 249 players), `"emerging"` ($< 50$ balls, 526 players), or `"all"` (775 players).
  - `sort_by` (`str`, default `"clutch_iq"`): Field to sort by (`clutch_iq`, `strike_rate`, `balls_faced`, `total_runs`, `batting_average`, `raw_delta_strike_rate`, `dot_ball_pct`, `boundary_ball_pct`).
  - `sort_order` (`str`, default `"desc"`): Sort direction (`"asc"`, `"desc"`).
  - `search` (`str`, optional): Case-insensitive player name substring filter.
  - `min_balls` (`int`, optional): Minimum pressure balls faced threshold.
  - `min_matches` (`int`, optional): Minimum distinct pressure matches.
- **Response**: `200 OK`
```json
{
  "items": [
    {
      "player_id": 2533,
      "player_name": "Najibullah Zadran",
      "rank": 1,
      "clutch_iq": 96.59,
      "cohort": "primary",
      "assignment_status": "fitted",
      "archetype_name": "Explosive Pressure Finishers & Boundary Hitters",
      "balls_faced": 62,
      "match_count": 8,
      "total_runs": 140,
      "strike_rate": 225.81,
      "batting_average": 46.67,
      "raw_delta_strike_rate": 84.85,
      "dot_ball_pct": 27.42,
      "boundary_ball_pct": 32.26,
      "reliability_weight": 0.58
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_records": 249,
    "total_pages": 13,
    "has_next": true,
    "has_prev": false
  }
}
```

#### `GET /api/v1/leaderboards/bowlers`
Returns a paginated list of bowlers ranked by Clutch IQ.
- **Query Parameters**: Same as batters, with bowling-specific sort fields (`clutch_iq`, `economy_rate`, `legal_balls`, `runs_conceded`, `bowler_wickets`, `bowling_strike_rate`, `bowling_average`, `raw_delta_economy`, `dot_ball_pct`, `boundary_balls_conceded_per_100_legal_balls`).
- **Response**: `200 OK`
```json
{
  "items": [
    {
      "player_id": 7327,
      "player_name": "Rasikh Salam",
      "rank": 1,
      "clutch_iq": 76.84,
      "cohort": "primary",
      "assignment_status": "fitted",
      "archetype_name": "Economical Pressure Controllers",
      "legal_balls": 66,
      "match_count": 8,
      "runs_conceded": 89,
      "bowler_wickets": 8,
      "economy_rate": 8.09,
      "bowling_strike_rate": 8.25,
      "bowling_average": 11.12,
      "raw_delta_economy": 1.74,
      "dot_ball_pct": 39.39,
      "boundary_balls_conceded_per_100_legal_balls": 15.15,
      "reliability_weight": 0.60
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_records": 219,
    "total_pages": 11,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### 4.3 Players

#### `GET /api/v1/players/{player_id}`
Returns high-level player profile, franchise associations, and profile existence flags.
- **Path Parameter**: `player_id` (`int`, required).
- **Response**: `200 OK`
```json
{
  "player_id": 23,
  "player_name": "Piyush Chawla",
  "teams": ["Mumbai Indians"],
  "competitions": ["IPL 2023", "IPL 2024"],
  "has_batting_profile": true,
  "has_bowling_profile": true,
  "batting_clutch_iq": 43.98,
  "bowling_clutch_iq": 43.43,
  "batting_rank": null,
  "bowling_rank": 91,
  "batting_archetype": "Pressure-Struggling / Low-Tempo Batters",
  "bowling_archetype": "Moderate-Containment / Mid-Tier Pressure Bowlers",
  "batting_cohort": "emerging",
  "bowling_cohort": "primary",
  "batting_assignment_status": "provisional",
  "bowling_assignment_status": "fitted"
}
```

#### `GET /api/v1/players/{player_id}/batting`
Returns full pressure batting profile, baseline comparison, regularized deltas, and archetype explanations.
- **Path Parameter**: `player_id` (`int`, required).
- **Error Codes**: `404 Not Found` if player does not exist or has no recorded pressure batting data.
- **Response**: `200 OK`
```json
{
  "player_id": 2533,
  "player_name": "Najibullah Zadran",
  "teams": ["Afghanistan"],
  "competitions": ["Asia Cup 2022", "T20I Series"],
  "clutch_iq": 96.59,
  "rank": 1,
  "cohort": "primary",
  "assignment_status": "fitted",
  "archetype_name": "Explosive Pressure Finishers & Boundary Hitters",
  "player_archetype_explanation": "Najibullah Zadran is characterized by elite boundary striking...",
  "balls_faced": 62,
  "total_runs": 140,
  "dismissals": 3,
  "not_outs": 5,
  "innings_count": 8,
  "match_count": 8,
  "strike_rate": 225.81,
  "batting_average": 46.67,
  "dot_ball_pct": 27.42,
  "boundary_ball_pct": 32.26,
  "fours": 8,
  "sixes": 12,
  "balls_baseline": 353,
  "runs_baseline": 477,
  "sr_baseline": 135.13,
  "avg_baseline": 34.07,
  "dot_pct_baseline": 32.86,
  "boundary_pct_baseline": 16.71,
  "reg_sr_base": 140.96,
  "raw_delta_strike_rate": 84.85,
  "shrunk_delta_strike_rate": 49.21,
  "reliability_weight": 0.58
}
```

#### `GET /api/v1/players/{player_id}/bowling`
Returns full pressure bowling profile, baseline comparison, regularized deltas, and archetype explanations.
- **Path Parameter**: `player_id` (`int`, required).
- **Error Codes**: `404 Not Found` if player does not exist or has no recorded pressure bowling data.
- **Response**: `200 OK`
```json
{
  "player_id": 7327,
  "player_name": "Rasikh Salam",
  "teams": ["Delhi Capitals"],
  "competitions": ["IPL 2024"],
  "clutch_iq": 76.84,
  "rank": 1,
  "cohort": "primary",
  "assignment_status": "fitted",
  "archetype_name": "Economical Pressure Controllers",
  "player_archetype_explanation": "Rasikh Salam demonstrates extraordinary run containment...",
  "legal_balls": 66,
  "runs_conceded": 89,
  "bowler_wickets": 8,
  "economy_rate": 8.09,
  "bowling_strike_rate": 8.25,
  "bowling_average": 11.12,
  "wickets_per_legal_ball": 0.1212,
  "dot_ball_pct": 39.39,
  "boundary_balls_conceded_per_100_legal_balls": 15.15,
  "fours_conceded": 6,
  "sixes_conceded": 4,
  "match_count": 8,
  "balls_baseline": 102,
  "runs_conceded_baseline": 178,
  "wickets_baseline": 5,
  "econ_baseline": 10.47,
  "wkt_sr_baseline": 20.4,
  "dot_pct_baseline": 31.37,
  "boundary_balls_per_100_baseline": 21.57,
  "reg_econ_base": 9.83,
  "raw_delta_economy": 1.74,
  "shrunk_delta_economy": 1.04,
  "reliability_weight": 0.60
}
```

#### `GET /api/v1/players/compare`
Compares 2 to 5 players side-by-side using comma-separated IDs.
- **Query Parameters**: `player_ids` (`str`, required, e.g. `?player_ids=2533,7327,23`).
- **Validation Rules**:
  - Requires between 2 and 5 unique, valid player IDs.
  - Returns `400 Bad Request` if $< 2$ or $> 5$ unique IDs provided.
  - Returns `404 Not Found` if any player ID is not registered.
- **Response**: `200 OK`
```json
{
  "players": [
    {
      "player_id": 2533,
      "player_name": "Najibullah Zadran",
      "teams": ["Afghanistan"],
      "batting": { ... },
      "bowling": null
    },
    {
      "player_id": 7327,
      "player_name": "Rasikh Salam",
      "teams": ["Delhi Capitals"],
      "batting": null,
      "bowling": { ... }
    }
  ],
  "compared_count": 2
}
```

---

### 4.4 Archetypes

#### `GET /api/v1/archetypes/batting`
Returns all 3 unsupervised K-Means batting archetype profiles, centroids, empirical strengths, weaknesses, and scouting narratives.
- **Response**: `200 OK` (List of 3 `BattingArchetypeProfile` objects).

#### `GET /api/v1/archetypes/batting/{cluster_id}`
Returns details for a specific batting archetype along with a paginated list of assigned players sorted by Clutch IQ.
- **Path Parameter**: `cluster_id` (`int`, 0, 1, or 2).
- **Query Parameters**: `page` (`int`, default `1`), `page_size` (`int`, default `20`).
- **Response**: `200 OK`

#### `GET /api/v1/archetypes/bowling`
Returns all 3 unsupervised K-Means bowling archetype profiles, centroids, empirical strengths, weaknesses, and scouting narratives.
- **Response**: `200 OK` (List of 3 `BowlingArchetypeProfile` objects).

#### `GET /api/v1/archetypes/bowling/{cluster_id}`
Returns details for a specific bowling archetype along with a paginated list of assigned players sorted by Clutch IQ.
- **Path Parameter**: `cluster_id` (`int`, 0, 1, or 2).
- **Query Parameters**: `page` (`int`, default `1`), `page_size` (`int`, default `20`).
- **Response**: `200 OK`

---

### 4.5 Macro Analytics & Pressure Segments

#### `GET /api/v1/analytics/summary`
Macro dataset summary providing full delivery, match, run, extras, and wicket totals.
- **Response**: `200 OK`
```json
{
  "total_matches": 883,
  "completed_matches": 843,
  "abandoned_matches": 40,
  "total_deliveries": 200999,
  "regular_innings_deliveries": 200961,
  "super_over_deliveries": 38,
  "total_team_runs": 281418,
  "total_batter_runs": 269506,
  "total_extras_runs": 11912,
  "total_bowler_wickets": 10261,
  "total_batters_count": 888,
  "total_bowlers_count": 647,
  "pressure_deliveries_count": 53453,
  "baseline_deliveries_count": 147508,
  "pressure_percentage": 26.6,
  "seasons_covered": ["2021/22", "2022", "2022/23", "2023", "2024"],
  "competitions_count": 14
}
```

#### `GET /api/v1/analytics/pressure`
Returns empirical metrics across all 8 segmented cricket environments.
- **Segments Returned**:
  1. `Overall Regular (Innings 1-2)` (200,961 deliveries)
  2. `Non-Pressure Baseline` (147,508 deliveries)
  3. `Death Overs Primary (16-20)` (44,792 deliveries)
  4. `Death Overs Strict (17-20)` (34,714 deliveries)
  5. `Close Chases (RRR >= 9, <= 36 balls)` (8,604 deliveries)
  6. `Knockout Deliveries` (10,724 deliveries)
  7. `Any Pressure (Union)` (53,453 deliveries)
  8. `Super Overs (Innings >= 3)` (38 deliveries — quarantined)
- **Mathematical Reconciliation**:
  $$\text{Non-Pressure Baseline (147,508)} + \text{Any Pressure Union (53,453)} = \text{Overall Regular (200,961)}$$
- **Response**: `200 OK`

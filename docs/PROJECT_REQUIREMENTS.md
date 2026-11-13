# SUPER RR — CLUTCH IQ: Project Requirements & Problem Statement

## 1. Executive Summary & Context

This project is developed for **SupeRR Selector Season 2: Identify the Most Reliable Players Under Pressure**, organized by the Rajasthan Royals.

Traditional cricket statistics (batting average, raw strike rate, overall economy rate) treat all deliveries equally. A six hit in the 3rd over of a low-stakes bilateral game counts the same in traditional statistics as a boundary hit off the final ball requiring 4 runs to win an IPL playoff. In high-performance sports analytics and franchise recruitment, identifying players who elevate their performance under intense psychological and match-situation pressure—**"Clutch" players**—is of paramount importance.

The objective of **SUPER RR — CLUTCH IQ** is to build a rigorous, fully transparent, data-driven system and interactive web application that measures how batters and bowlers perform in defined high-pressure situations relative to their standard baseline performance, discovering the true clutch performers from 2022 onwards across IPL and T20 International cricket.

---

## 2. Official Competition Requirements (SupeRR Selector Season 2)

Based directly on the official problem statement (`data/raw/Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf`), the core deliverables and criteria are:

### Deliverable 1: Two Ordered Top-10 Lists
1. **Top 10 Batters Under Pressure**: Ordered Rank 1 to 10 (Rank 1 being the highest-rated clutch batter).
2. **Top 10 Bowlers Under Pressure**: Ordered Rank 1 to 10 (Rank 1 being the highest-rated clutch bowler).
*Constraints:*
- No repeated players within the same top-10 list.
- Rankings must be supported by empirical analysis of the supplied data, not reputation or fame.
- Selections must match the methodology report.

### Deliverable 2: Comprehensive Methodology Report
The uploaded document must clearly cover:
1. **Pressure Definition**: The specific match situations, indicators, and thresholds used, and the biological/cricketing rationale behind them.
2. **Performance Measurement**: Batting and bowling metrics, baseline calculation logic, and relative scoring formulas.
3. **Fair Comparisons**: Sample size adjustments, player eligibility criteria, context adjustments (IPL vs. T20I, home vs. away, target difficulty).
4. **Evidence for Top 10**: Transparent tabular comparisons, charts, and ball-by-ball evidence supporting each selection and ranking order.
5. **Reliability and Limitations**: Robustness checks across matches and seasons, sensitivity analysis, and explicit acknowledgment of edge cases and model uncertainties.

---

## 3. Web Application Scope & Feature Requirements

To make the analysis professional, demonstrable, and interactive, the project includes a full-stack web application:

### 3.1 Core Modules
1. **Clutch Leaderboard (Top 10 & Global Player Search)**:
   - Separate ranked views for Batters and Bowlers.
   - Filterable by Competition Type (All, IPL Only, T20I Only), Season (2022–2026), and Pressure Context.
   - Expandable breakdown card for every player showing rank, Clutch IQ score, Baseline vs. Pressure delta, and key metrics.

2. **Player Deep-Dive Profile**:
   - Radar chart (Plotly) comparing Baseline vs. Clutch attributes (Strike Rate, Dot Ball %, Boundary %, Wicket Hazard, Economy, Dot % Under Pressure).
   - Ball-by-ball pressure shot breakdown (for batters) and line/length/speed breakdown (where reliable).
   - Match log of clutch performances (Super Overs, knockout matches, last-over finishes).

3. **Pressure Dimension Analysis**:
   - Independent analysis of the three core pressure categories:
     * **Death Overs** (Overs 17–20 / 16–20).
     * **Close Chases** (Innings 2 high Required Run Rate / tight victory margin).
     * **Knockout Matches** (Playoffs, Semi-Finals, Finals).
   - Interactive toggle to explore player ratings across each pressure dimension individually.

4. **Machine Learning Archetype Explorer (K-Means Clustering)**:
   - Separate clustering pipelines for batters and bowlers.
   - Interactive 2D/3D PCA visualization showing player clusters (e.g., "Elite Ice-in-the-Veins Finishers", "Steady Anchors", "Powerplay Specialists", "Death Choke Bowlers").
   - Statistical evaluation (Elbow curve, Silhouette scores) and plain-English cluster interpretations.

5. **Head-to-Head Clutch Comparison**:
   - Side-by-side comparison tool of any two players under pressure.

---

## 4. Technical Constraints & Working Principles

1. **100% Free Technology Stack**:
   - Frontend: React, Vite, Tailwind CSS, Lucide React icons, Plotly.js (`react-plotly.js`).
   - Backend: Python 3.13+, FastAPI, Uvicorn, Pydantic v2.
   - Analytics & ML: Pandas, NumPy, Scikit-learn (KMeans, StandardScaler, PCA).
   - Storage/Cache: Parquet / SQLite (lightweight local database, no paid services).
   - No paid APIs, no external subscriptions, no third-party paywalls.

2. **Data Integrity & Traceability Rules**:
   - **Zero Hallucination / Zero Fabrication**: Never invent statistics, ranks, or machine-learning outputs.
   - **Original Files Protected**: Never modify, overwrite, or delete raw CSV files in `data/raw/`.
   - **Reproducibility**: All metrics, rankings, and clusters must be 100% reproducible via reproducible code scripts from raw data.
   - **Super Over Isolation**: Innings 3 & 4 must be analyzed as separate high-pressure events, not mixed into 20-over averages.
   - **Official Cricket Rules**: Strictly respect legal balls (wides and no-balls do not count as legal balls bowled or balls faced) and bowler-creditable wickets (Run Outs, Retire Outs, and Obstructing the Field must not be credited to bowlers).

---

## 5. Metrics Calculation Feasibility Matrix

| Metric Category | Metric Name | Feasible from Data? | Calculation Method / Source | Notes & Limitations |
| :--- | :--- | :---: | :--- | :--- |
| **Batting** | Batting Strike Rate (SR) | **Yes** | `(runs / legal_balls_faced) * 100` | Excludes wides; no-balls counted for runs but not legal balls faced |
| **Batting** | Batting Average | **Yes** | `runs / dismissals` | Verified against `dismissed_player_id == player_id` |
| **Batting** | Boundary % (Balls / Runs) | **Yes** | `is_four`, `is_six` | Exact from ball-by-ball boolean flags |
| **Batting** | Dot Ball % Faced | **Yes** | Balls with `runs == 0` & `extras_type.isna()` | High reliability |
| **Batting** | Non-Boundary Strike Rate | **Yes** | Strike rate on 1s, 2s, 3s | Crucial for rotating strike under pressure |
| **Bowling** | Bowling Economy Rate (Econ) | **Yes** | `(runs_conceded / legal_balls) * 6` | Bowler runs = bat runs + wides + noball penalty; excludes byes & legbyes |
| **Bowling** | Bowling Average | **Yes** | `runs_conceded / bowler_wickets` | Only bowler-creditable dismissals |
| **Bowling** | Bowling Strike Rate | **Yes** | `legal_balls / bowler_wickets` | Legal deliveries per wicket |
| **Bowling** | Dot Ball % Bowled | **Yes** | Legal balls conceding 0 runs | High pressure indicator |
| **Bowling** | Boundary Conceded % | **Yes** | Balls conceding 4 or 6 / total legal balls | Critical death-over defense metric |
| **Context** | Death Overs Splits | **Yes** | `overid >= 17` (or `>= 16`) | Available on all 200,999 deliveries |
| **Context** | Knockout Filter | **Yes** | `matches.knock_out == 1` | 31 matches (Finals, Semis, Eliminators, Qualifiers) |
| **Context** | Close Chases | **Yes** | `innings == 2` + margin <= 15 runs / <= 3 wkts / over 20 | Verified from match outcomes & ball sequence |
| **Context** | Super Over Heroics | **Yes** | `innings >= 3` | 6 matches, 38 deliveries |
| **Physical** | Bowling Speed / Release Velocity | **Unreliable** | `bowl_speed` column | 38.7% missing/0; negative values; 1456 km/h outliers. Cannot be used for rankings. |
| **Physical** | Shot Type / Stroke Mechanics | **Partial** | `stroke` column | 6,158 missing values (~3.1%). Good for qualitative insights, not primary ranking. |
| **Fielding**| Catches, Run-out Assists | **No** | Not present | No `fielder_id` or `catcher_id` in raw dataset |

# SUPER RR — CLUTCH IQ: Comprehensive Dataset Audit Report (Updated & Validated)

**Date of Audit**: November 2026 (Updated after Phase 0 review & validation)  
**Dataset Path**: `data/raw/`  

---

## 1. Executive Summary & Validation Status

A rigorous programmatic audit was conducted on all six dataset CSV files and the problem statement PDF. Following user feedback, ten specific cricket and data-engineering hypotheses were thoroughly tested against match scorecards and delivery-level data.

### Validation Status Summary:
- **`extras1_runs` Decoded**: Validated as an integer category code for `extras_type` (1=Overstep, 2=wide, 3=legbyes, 4=byes, 5=other, 6=None, 7=Penalty). Summing this column directly would corrupt all statistics.
- **`extras_2_runs` Investigated**: Occurs in only 36 deliveries. All 36 rows correspond to no-balls (`Overstep`, `other`, or rare unclassified) where the batter played a stroke (e.g. leg glance, cut, pull) and the ball traveled for byes, leg-byes, or overthrows (1 or 4 runs) with `runs == 0`. Under standard cricket rules, fielding byes/leg-byes off a no-ball are not charged against the bowler. We document this and conservatively exclude `extras_2_runs` from bowler runs conceded.
- **Revised Overs Values are BALLS, not Overs**: Programmatically proven using the IPL 2023 Final (Match 21586) and 33 other matches. A value of `90.0` represents 90 balls (15 overs), NOT 90 overs.
- **Reconciliation of Revised Matches**: Exactly 34 matches contain revised data across `first_inn_revised_overs` (25 matches), `second_inn_revised_overs` (25 matches), and `revised_target` (23 matches). The union is exactly 34 matches.
- **Playing XI Duplicates Resolved**: 75 duplicate rows in `playing_eleven.csv` occur across exactly 3 matches (13613, 21176, 28962). All have `is_impact == 0` and represent conflicting lineup sheet versions where only `batting_order` differs.
- **Batter Dismissals & Non-Striker Run Outs**: In 274 dismissals, the non-striker was out. In row 127899 (Match 40709), Tilak Varma retired out (non-striker). Tracking `dismissed_player_id == player_id` captures 100% of dismissals.
- **Legal Delivery Identification**: `over_ball_num` is the sequential delivery counter (reaching 7, 8, 9 on extras), NOT the legal ball count. A legal delivery is strictly defined as `extras_type` not in `['wide', 'Overstep', 'other']`. Across 31,757 completed overs, exactly 6 legal balls were bowled.
- **Bowler-Credited Wickets**: Exactly 10,272 out of 10,881 dismissals are credited to bowlers (Bowled, Caught, LBW, Stump, Hit Wicket). RunOut (600), Retire Out (6), and Obstructing the field (3, including 2 misspelled as *"Obstracting"*) are excluded.
- **Super Overs Isolated**: 6 matches (38 balls) contain Super Overs (`innings >= 3`). They are segregated from 20-over rate statistics.
- **Outcome Leakage Avoidance**: Close chase pressure is defined purely through situational in-match context (Innings 2, $\le 36$ balls remaining, Required Run Rate $\ge 9.0$), rather than retrospectively labeling early deliveries based on final victory margins.

---

## 2. File Inventory & Dimension Verification

| # | File Name | File Size | Actual Rows | Actual Columns | Primary Key / Grain | Integrity Status |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `competitions.csv` | 7.44 KB | 141 | 4 | `comp_id` | Validated (100% unique) |
| 2 | `teams.csv` | 6.76 KB | 353 | 3 | `(comp_id, team_id)` | Validated (100% unique) |
| 3 | `matches.csv` | 120.96 KB | 883 | 22 | `match_id` | Validated (100% unique) |
| 4 | `competition_team_player_mapping.csv` | 452.12 KB | 6,413 | 6 | `(comp_id, team_id, player_id)` | Validated (100% unique) |
| 5 | `playing_eleven.csv` | 943.64 KB | 28,381 | 9 | `(match_id, player_id)` | 75 duplicate lineup sheet rows in 3 matches |
| 6 | `ball_by_ball.csv` | 39.17 MB | 200,999 | 33 | `(match_id, innings, innings_ball_num)` | Validated (100% unique) |
| 7 | `Round 1 Problem Statement...pdf` | 248.13 KB | 2 pages | Spec / Brief | Problem Statement Document | Requirements Extracted |

---

## 3. Deep-Dive Validation of the 10 Investigation Points

### Point 1 & 3: Bowler Runs Conceded, Extras & Investigation of `extras_2_runs`
- **Bowler Runs Conceded Formula**:
  $$\text{Bowler Runs} = \text{runs (off the bat)} + \text{wide penalty (1 run)} + \text{no-ball penalty (1 run for Overstep or other)}$$
- **Byes & Legbyes**:
  Fielding extras (byes and legbyes) are **strictly excluded** from bowler runs conceded in accordance with MCC Law 21 and standard T20 scoring rules.
- **Investigation of `extras_2_runs`**:
  - Exactly 36 rows in the entire 200,999-row dataset have `extras_2_runs > 0` (16 rows with `1`, 20 rows with `4`).
  - All 36 rows occurred on no-balls (`Overstep` = 21, `other` = 14, unclassified = 1) where `runs == 0` and the batter played a stroke (e.g. Row 90205: Yash Dayal to Andre Russell, `extras_type = Overstep`, `stroke = Leg Glance`, `extras_2_runs = 4`).
  - These represent boundary/running leg-byes or overthrows resulting from an illegal delivery.
  - **Decision**: In standard cricket, runs resulting from leg-byes or overthrows off a no-ball are not charged to the bowler's individual figures (only the 1-run no-ball penalty is charged). Therefore, `extras_2_runs` is **conservatively excluded** from bowler runs conceded to maintain strict compliance with official scoring figures.

### Point 2: Legal Ball Identification
- **`over_ball_num` Warning**: `over_ball_num` records the sequential delivery count in an over. Whenever a wide or no-ball is bowled, the delivery must be re-bowled, causing `over_ball_num` to increment to 7, 8, or 9. **It cannot be used as the legal-ball count.**
- **Validated Legal Ball Definition**:
  $$\text{is\_legal\_ball} = \text{extras\_type} \notin [\text{'wide'}, \text{'Overstep'}, \text{'other'}]$$
- **Empirical Validation**:
  - Across 31,757 completed overs in the dataset, this definition produces **exactly 6.0 legal balls per over**.
  - In 589 out of 592 overs with $< 6$ legal balls, the over was the final over of the match/innings where the target was achieved or the team was bowled out.

### Point 4: Revised Overs Values Represent BALLS, Not Overs
- **Empirical Proof**:
  - In Match 21586 (IPL 2023 Final: CSK vs GT), the match was rain-interrupted. CSK was famously set a DLS target of 171 in **15 overs (90 balls)**.
  - In `matches.csv`, row 262: `second_inn_revised_overs = 90.0`, `revised_target = 171.0`.
  - In Match 17395 (India vs Australia 2022, 8-over rain-reduced match): `first_inn_revised_overs = 48.0` and `second_inn_revised_overs = 48.0` (48 balls = 8 overs).
  - Every non-null value in these columns is an exact multiple of 6 (30, 42, 48, 54, 60, 66, 72, 78, 84, 90, 102, 108, 114).
- **Rule**: To compute revised overs, we must divide by 6:
  $$\text{revised\_overs} = \frac{\text{revised\_balls}}{6.0}$$

### Point 5: Investigation of 75 Duplicate Playing XI Records
- **Findings**:
  - Occurs across only 3 matches: Match 13613 (24 rows), Match 21176 (22 rows), and Match 28962 (29 rows).
  - All 75 rows have `is_impact == 0` and `is_impact_off == 0`. They are **not impact substitutions**.
  - All players have `is_played == True`.
  - The duplicate rows are identical in player ID, team ID, captain status, and wicketkeeper status. They differ **only in preliminary `batting_order`** (e.g. Player 223 listed at order 5.0 and order 6.0).
  - This was caused by multiple preliminary lineup card revisions being logged for those three matches.
- **Handling**: Deduplicate cleanly using `drop_duplicates(subset=['match_id', 'player_id'], keep='first')`.

### Point 6: Reconciliation of Revised Matches
- `first_inn_revised_overs` non-null: **25 matches**
- `second_inn_revised_overs` non-null: **25 matches**
- `revised_target` non-null: **23 matches**
- **Union of any of the three**: **34 matches**
- **Exact Venn Breakdown**:
  - All 3 present: **14 matches** (Rain affected both innings, target revised).
  - Only `second_inn_revised_overs` & `revised_target`: **9 matches** (1st innings full 20 overs, rain interrupted only 2nd innings).
  - Only `first_inn_revised_overs`: **9 matches** (Rain shortened 1st innings; match abandoned before 2nd innings).
  - Both `first` and `second_inn_revised_overs` present, but no `revised_target`: **2 matches** (Matches 46311 and 50408; abandoned mid-game as "No Result").
  - `revised_target` without revised overs: **0 matches**.

### Point 7: Batter Dismissals & Non-Striker Run-Outs
- Wicket events (`is_wicket == True`): 10,881 rows.
- Striker dismissed (`dismissed_player_id == striker_id`): 10,606 rows.
- Non-striker dismissed (`dismissed_player_id == non_striker_id`): **274 rows** (run outs at non-striker's end).
- Anomaly check: Row 127899 (Match 40709, MI vs LSG, May 17 2024): `dismissal_type = Retire Out`, `dismissed_player_id` was NaN. Sequential ball tracking confirms Tilak Varma took a single on ball 19.4, retired out on ball 19.5, and was replaced by Mitchell Santner on ball 19.6. We resolve `dismissed_player_id` for row 127899 as 7897 (Tilak Varma).
- **Rule**: Batter dismissals must be counted strictly as `dismissed_player_id == player_id`.

### Point 8: Bowler-Creditable Dismissals
- Validated categories:
  - `Bowled`: 1,775
  - `Caught`: 7,557
  - `LBW`: 709
  - `Stump`: 214
  - `Hit Wicket`: 17
  - **Total Bowler Wickets**: **10,272**
- Non-bowler dismissals:
  - `RunOut`: 600
  - `Retire Out`: 6
  - `Obstructing the field`: 1
  - `Obstracting the field`: 2 (spelling variation in raw data mapped to obstructing)
  - **Total Non-Bowler Wickets**: **609**

### Point 9: Super Over Isolation
- Six matches feature Super Overs (`innings >= 3`): Matches 34429, 40725, 45512, 48027, 48029, 50359.
- Total deliveries: 38 (25 in Innings 3; 13 in Innings 4).
- **Pipeline Treatment**: A boolean column `is_super_over = innings >= 3` ensures Super Overs are never conflated with regular innings averages, while remaining queryable as distinct tiebreak pressure moments.

### Point 10: Documented Assumptions & Validation Status Matrix

| Analytical Metric / Feature | Validation Status | Governing Assumption / Limitation |
| :--- | :---: | :--- |
| **Batter Runs & Balls Faced** | **High Confidence** | Excludes wides; no-balls count towards runs but not balls faced. |
| **Bowler Runs Conceded** | **High Confidence** | Includes bat runs + wides (1) + no-balls (1); excludes byes, leg-byes, and `extras_2_runs`. |
| **Bowler Wickets** | **High Confidence** | Exactly 10,272 bowler-creditable dismissals. Run outs and retire outs excluded. |
| **Over Identification** | **High Confidence** | `overid` is 1-indexed (1 to 20). Death overs primary: 16–20; stricter: 17–20. |
| **Legal Delivery Count** | **High Confidence** | `is_legal_ball = ~extras_type.isin(['wide', 'Overstep', 'other'])`. Verified against 31,757 overs. |
| **Team Score Reconstruction** | **Moderate Confidence** | Reconstructed total scores match official match margins within 1–3 runs due to rare unrecorded multi-run byes/leg-byes. |
| **Close Chase Pressure** | **High Confidence** | Situational only: Innings 2, legal balls remaining $\le 36$, Required Run Rate $\ge 9.0$. Zero outcome leakage. |
| **Bowling Speed (`bowl_speed`)** | **Unvalidated / Excluded** | 38.7% missing/zero; negative values; extreme sensor outliers (up to 1456 km/h). |
| **Stroke (`stroke`)** | **Descriptive Only** | 3.1% missing; useful for qualitative shot profiles, not for primary ranking. |
| **Fielding Metrics** | **Unavailable** | Fielder IDs are absent from the dataset. |

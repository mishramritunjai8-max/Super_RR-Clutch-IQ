# Phase 4 Methodology: Machine Learning & Player Profiling via K-Means Clustering (Corrected Final Version)

**Project**: SUPER RR — CLUTCH IQ: Beyond Statistics. Discovering Players Who Perform Under Pressure  
**Season / Context**: SupeRR Selector Season 2 (Rajasthan Royals Hackathon)  
**Author**: Antigravity Senior Machine Learning Engineer, Cricket Data Scientist & Software Architect  
**Status**: APPROVED & FULLY RE-AUDITED (Phase 4 Complete)  
**Engine Version**: `4.1.0` (Supersedes Version `4.0.0`)  

---

> [!IMPORTANT]
> **SUPERSEDED VERSION NOTICE**: This document represents the corrected, finalized Phase 4 machine learning methodology (Engine Version `4.1.0`). All preliminary findings from Version `4.0.0`—specifically the collinear 7-feature spaces, arbitrary zero-denominator imputations (such as substituting runs for average or legal balls for strike rate), initial $K=4$ batting partition, and unsupported tactical over-by-over assignments—have been formally deprecated, corrected, retrained, and replaced.

---

## 1. Executive Summary

Phase 4 operationalizes unsupervised machine learning to group professional T20 cricket players into intuitive, statistically verified, and tactically actionable **cricket player archetypes** based strictly on their delivery-level pressure vs. baseline performance profiles.

While Phase 3 established *how much* a player elevates under pressure through the Bayesian-regularized **Clutch IQ Score**, Phase 4 uncovers *how* players behave structurally:
- **Batters**: Segmenting players into **Explosive Pressure Finishers & Boundary Hitters** (e.g., Tristan Stubbs, MS Dhoni, Tim David) versus **Steady Pressure Anchors & Strike Rotators** (e.g., Clive Madande, Karim Janat, Hardik Pandya) versus **Pressure-Struggling / Low-Tempo Batters** (e.g., Shaheen Afridi, Rahul Chahar, Shoriful Islam).
- **Bowlers**: Segmenting players into **Economical Pressure Controllers** (e.g., Sunil Narine, Pramod Madushan, Rasikh Salam) versus **Moderate-Containment / Mid-Tier Pressure Bowlers** (e.g., Arshdeep Singh, Mohammed Siraj) versus **Pressure-Vulnerable / High-Concession Bowlers** (e.g., Tushar Deshpande, Mukesh Kumar, Patrick Cummins).

### Key Methodological Corrections Implemented in Version `4.1.0`
1. **Elimination of Mathematically Redundant Features**: Cured exact algebraic identities ($\Delta \text{SR} \equiv \text{SR} - \text{reg\_sr\_base}$ and $\Delta \text{Econ} \equiv \text{reg\_econ\_base} - \text{Econ}$) and collinear deltas ($\Delta \text{Dot\%}$), reducing condition numbers from $\sim 10^{16}$ down to stable condition numbers ($151.95$ for Batting, $105.22$ for Bowling).
2. **Mathematically Sound Zero-Dismissal & Zero-Wicket Treatment**:
   - For Batters with 0 dismissals: Preserved original `batting_average` as `NaN`, introduced an explicit `is_zero_dismissals` indicator, and imputed missing values using the primary cohort median ($20.93$) strictly fitted on primary players.
   - For Bowlers with 0 wickets: Preserved original `bowling_strike_rate` as `NaN`, introduced an `is_zero_wickets` indicator, and adopted `wickets_per_legal_ball` as a continuous, everywhere-defined rate ($0.0$ for zero-wicket bowlers), eliminating the division-by-zero divergence of strike rate.
3. **Rigorous Re-Evaluation of Candidate $K$**:
   - Re-evaluated $K \in [2, 8]$ across Silhouette, Davies-Bouldin, Calinski-Harabasz, Inertia, and Cluster Balance.
   - Selected **$K = 3$ for Batting** (Silhouette 0.3070, Balance Ratio 0.4167), replacing the previous flawed $K=4$ which contained an unstable 11-player micro-cluster.
   - Selected **$K = 3$ for Bowling** (Silhouette 0.2263, Balance Ratio 0.4404), rigorously documenting the practical scouting necessity of separating controllers from strike/mid-tier bowlers despite $K=2$ having a higher silhouette.
4. **Removal of Unsupported Tactical Claims**: Stripped out fabricated over-by-over claims (such as assigning bowlers specifically to overs 16 and 18) and powerplay claims, replacing them with sound scouting hypotheses ("candidate profile", "potential tactical role").
5. **Decoupled Clutch IQ**: Verified that Clutch IQ, rankings, and Top 10 indicators were strictly withheld from model training and attached purely post-hoc for external validation.

---

## 2. Feature Engineering & Redundancy Removal

To ensure K-Means isotropic Euclidean distances reflect genuine multi-dimensional performance without artificially double-weighting redundant axes, proposed features were audited for exact collinearity and high pairwise correlations.

### 2.1 The Redundancy Pathology & Correction

In initial prototypes, the feature sets contained exact algebraic relationships:
- **Batting**: $\text{raw\_delta\_strike\_rate} \equiv \text{strike\_rate} - \text{reg\_sr\_base}$
- **Bowling**: $\text{raw\_delta\_economy} \equiv \text{reg\_econ\_base} - \text{economy\_rate}$

Because any third variable is an exact linear combination of the other two, including all three in Euclidean distance gave double weight to the scoring velocity dimension, driving the correlation matrix condition number to $2.11 \times 10^{16}$ (Batting) and $9.62 \times 10^{17}$ (Bowling).

Furthermore, $\text{raw\_delta\_dot\_pct}$ exhibited near-collinearity with $\text{dot\_ball\_pct}$ ($\text{corr} = -0.834$ in Batting, $-0.835$ in Bowling) while representing another redundant baseline delta.

#### Diagnostic Impact of Redundancy Removal
| Model | Initial Condition Number | Corrected Condition Number | Determinant | Max Pairwise VIF | Status |
|---|:---:|:---:|:---:|:---:|:---:|
| **Batting** | $2.11 \times 10^{16}$ | **151.95** | $0.0066$ | $27.14$ | **CURED** |
| **Bowling** | $9.62 \times 10^{17}$ | **105.22** | $0.0095$ | $20.48$ | **CURED** |

---

### 2.2 Corrected Batting Feature Space ($\mathbb{R}^5$)

The corrected model retains a compact, interpretable 5-dimensional feature vector:

$$\mathbf{x}_{\text{bat}, i} = \begin{bmatrix} \text{strike\_rate}_i \\ \text{raw\_delta\_strike\_rate}_i \\ \text{dot\_ball\_pct}_i \\ \text{boundary\_ball\_pct}_i \\ \text{batting\_average\_imputed}_i \end{bmatrix} \in \mathbb{R}^5$$

1. **`strike_rate`**: Absolute pressure scoring tempo ($\frac{\text{Runs}}{\text{Balls Faced}} \times 100$). Excludes wides; includes no-balls.
2. **`raw_delta_strike_rate`**: Scoring acceleration shift under pressure ($\text{SR}_{\text{pressure}} - \text{SR}_{\text{base\_reg}}$). Measures clutch gear shift.
3. **`dot_ball_pct`**: Pressure dot-ball frequency ($\frac{\text{Dots}}{\text{Balls Faced}} \times 100$). Measures ball consumption.
4. **`boundary_ball_pct`**: Pressure boundary hitting frequency ($\frac{\text{Fours}+\text{Sixes}}{\text{Balls Faced}} \times 100$). Measures raw boundary power.
5. **`batting_average_imputed`**: Wicket preservation under pressure ($\frac{\text{Runs}}{\text{Dismissals}}$), with zero-dismissal cases imputed via the primary cohort median ($20.93$).

#### Excluded Batting Features:
- `reg_sr_base`: Excluded due to exact algebraic identity $\text{reg\_sr\_base} = \text{strike\_rate} - \text{raw\_delta\_strike\_rate}$.
- `raw_delta_dot_pct`: Excluded due to near-collinearity ($\text{corr} = -0.834$ with `dot_ball_pct`) and algebraic redundancy against `reg_dot_base`.

---

### 2.3 Corrected Bowling Feature Space ($\mathbb{R}^5$)

The corrected model retains a compact, interpretable 5-dimensional feature vector:

$$\mathbf{x}_{\text{bowl}, j} = \begin{bmatrix} \text{economy\_rate}_j \\ \text{raw\_delta\_economy}_j \\ \text{wickets\_per\_legal\_ball}_j \\ \text{dot\_ball\_pct}_j \\ \text{boundary\_balls\_conceded\_per\_100\_legal\_balls}_j \end{bmatrix} \in \mathbb{R}^5$$

1. **`economy_rate`**: Absolute pressure run containment per 6 legal balls ($\frac{\text{Bowler Runs}}{\text{Legal Balls}} \times 6.0$).
2. **`raw_delta_economy`**: Signed economy elevation ($\text{Econ}_{\text{base\_reg}} - \text{Econ}_{\text{pressure}}$). Positive indicates run suppression.
3. **`wickets_per_legal_ball`**: Continuous, everywhere-defined wicket potency rate ($\frac{\text{Bowler Wickets}}{\text{Legal Balls}}$). Exactly $0.0$ for zero-wicket bowlers.
4. **`dot_ball_pct`**: Dot-ball forcing percentage under pressure ($\frac{\text{Dots Bowled}}{\text{Legal Balls}} \times 100$).
5. **`boundary_balls_conceded_per_100_legal_balls`**: Frequency of boundary concession per 100 legal deliveries.

#### Excluded Bowling Features:
- `reg_econ_base`: Excluded due to exact algebraic identity $\text{reg\_econ\_base} = \text{economy\_rate} + \text{raw\_delta\_economy}$.
- `bowling_strike_rate`: Excluded due to division-by-zero divergence when wickets = 0. Replaced by continuous `wickets_per_legal_ball`.
- `raw_delta_dot_pct`: Excluded due to near-collinearity ($\text{corr} = -0.835$ with `dot_ball_pct`).

---

## 3. Zero-Denominator & Missing Value Policy

### 3.1 Batting: Zero Dismissals
In pressure overs, batters may face limited deliveries without being dismissed.
- **Primary Cohort ($\ge 50$ balls faced)**: Exactly $0$ out of $249$ primary batters have 0 dismissals ($100\%$ have $\ge 1$ dismissal). Thus, the training cohort contains zero missing values.
- **Emerging Cohort ($< 50$ balls faced)**: Exactly $102$ emerging batters have 0 dismissals.
- **Policy**:
  1. Do NOT set average equal to total runs (this is not an observed rate).
  2. Preserve original `batting_average` as `NaN` in datasets.
  3. Introduce `is_zero_dismissals` binary flag.
  4. Compute the primary cohort median:
     $$\text{Median}(\text{Avg}_{\text{primary}}) = 20.93\text{ runs / dismissal}$$
  5. Impute `batting_average_imputed` using this frozen primary median for emerging zero-dismissal batters. Emerging players are strictly excluded from computing this statistic.

### 3.2 Bowling: Zero Wickets
When a bowler delivers balls without taking a creditable wicket, bowling strike rate ($\frac{\text{Balls}}{\text{Wickets}}$) diverges to $\infty$.
- **Primary Cohort ($\ge 50$ legal balls)**: Exactly $3$ primary bowlers have 0 wickets under pressure (Ramesh Mendis, Curtis Campher, Nimesh Vimukthi).
- **Emerging Cohort ($< 50$ legal balls)**: Exactly $109$ emerging bowlers have 0 wickets.
- **Policy**:
  1. Do NOT substitute legal balls as observed strike rate.
  2. Preserve original `bowling_strike_rate` as `NaN` and add `is_zero_wickets` indicator.
  3. Utilize `wickets_per_legal_ball` as the model feature:
     $$\text{WicketsPerLegalBall} = \frac{\text{Bowler Wickets}}{\text{Legal Balls}}$$
     Since every bowler in the pressure dataset delivered at least 1 legal ball, this rate is bounded in $[0, 1]$, everywhere defined, non-divergent, and mathematically $0.0$ when wickets = 0.

---

## 4. Preprocessing & Cohort Separation Pipeline

### 4.1 Strict Anti-Leakage Protocol
1. **Primary Eligible Cohort ($\ge 50$ balls)**:
   - Batting: $N = 249$ qualified players.
   - Bowling: $N = 219$ qualified players.
   - All scalers (`StandardScaler`) and `KMeans` cluster centroids are fit **exclusively** on this cohort.
2. **Emerging Cohort ($< 50$ balls)**:
   - Batting: $N = 526$ players.
   - Bowling: $N = 324$ players.
   - Transformed using the frozen primary scaler parameters $(\boldsymbol{\mu}_{\text{primary}}, \boldsymbol{\sigma}_{\text{primary}})$.
   - Assigned to clusters via nearest Euclidean distance to the frozen primary centroids.
   - Labeled with `assignment_status = "provisional"`.

### 4.2 StandardScaler vs. RobustScaler Comparison
Both scalers were evaluated across candidate $K$:
- **StandardScaler**: Yields unit variance ($\mu=0, \sigma=1$), producing isotropic distance spaces that align with K-Means spherical variance assumptions.
- **RobustScaler**: Uses median and IQR; while robust to extreme outliers, it compressed high-performing clutch finishers closer to anchors.
- **Decision**: `StandardScaler` was adopted because the non-collinear 5-feature space exhibits well-behaved distributions without destructive outlier skewness once division-by-zero artifacts are eliminated.

---

## 5. Candidate $K$ Evaluations & Optimal Selection

Candidate $K \in [2, 8]$ was evaluated across Silhouette Score, Davies-Bouldin Index (DBI), Calinski-Harabasz Index (CHI), Inertia (WCSS), and Cluster Balance Ratio ($\min |C_k| / \max |C_k|$).

### 5.1 Batting Candidate Validation Results ($N = 249$ Primary Batters)

| $K$ | Silhouette | Davies-Bouldin | Calinski-Harabasz | Inertia | Min Size | Max Size | Balance Ratio | Cluster Sizes | Assessment |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|---|
| **2** | **0.3672** | **0.9864** | **192.08** | 700.37 | 101 | 148 | 0.6824 | `{0: 148, 1: 101}` | Binary split into above-average vs below-average; collapses finishers and anchors. |
| **3** | **0.3070** | **1.0809** | **170.80** | **521.22** | **45** | **108** | **0.4167** | **`{0: 45, 1: 96, 2: 108}`** | **OPTIMAL SELECTION**: Cleanly isolates Finishers (96), Anchors (108), and Strugglers (45) with healthy cluster sizes and zero micro-clusters. |
| **4** | 0.3218 | 1.0075 | 156.61 | 426.71 | 11 | 104 | 0.1058 | `{0: 11, 1: 104, 2: 89, 3: 45}` | **REJECTED**: Forms an unstable 11-player micro-cluster isolating high-average outliers (balance ratio plummets to 0.106). |
| **5** | 0.2982 | 1.0375 | 147.96 | 363.44 | 10 | 93 | 0.1075 | `{0: 10, 1: 16, 2: 93, 3: 52, 4: 78}` | Unstable micro-clusters ($N = 10$). |
| **6** | 0.2656 | 1.1230 | 135.52 | 328.63 | 9 | 73 | 0.1233 | `{0: 50, 1: 64, 2: 73, 3: 16, 4: 37, 5: 9}` | Severe fragmentation. |
| **7** | 0.2406 | 1.1938 | 129.31 | 296.00 | 9 | 62 | 0.1452 | `{0: 59, 1: 15, 2: 34, 3: 41, 4: 29, 5: 62, 6: 9}` | Severe fragmentation. |
| **8** | 0.2446 | 1.1902 | 122.15 | 273.76 | 9 | 55 | 0.1636 | `{0: 18, 1: 55, 2: 16, 3: 9, 4: 40, 5: 39, 6: 29, 7: 43}` | Severe noise fitting. |

**Rationale for Batting $K=3$**:
In the corrected 5-feature space, $K=3$ achieves a high silhouette score ($0.3070$) and excellent cluster balance ($45, 96, 108$, balance ratio $0.4167$). In contrast, $K=4$ creates an unstable 11-player micro-cluster consisting solely of batters with unusually high averages due to 1 or 2 total dismissals. Selecting $K=3$ provides a parsimonious, statistically robust, and tactically complete taxonomy.

---

### 5.2 Bowling Candidate Validation Results ($N = 219$ Primary Bowlers)

| $K$ | Silhouette | Davies-Bouldin | Calinski-Harabasz | Inertia | Min Size | Max Size | Balance Ratio | Cluster Sizes | Assessment |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|---|
| **2** | **0.2976** | **1.1774** | **121.77** | 701.41 | 109 | 110 | 0.9909 | `{0: 110, 1: 109}` | Highest mathematical silhouette; splits bowlers into binary expensive vs non-expensive halves. |
| **3** | **0.2263** | **1.3286** | **96.37** | **578.64** | **48** | **109** | **0.4404** | **`{0: 62, 1: 109, 2: 48}`** | **OPTIMAL SELECTION**: Captures Controllers (62), Mid-Tier Bowlers (109), and Vulnerable Bowlers (48) with solid balance (0.4404) and zero micro-clusters. |
| **4** | 0.2321 | 1.2567 | 89.13 | 488.05 | 25 | 98 | 0.2551 | `{0: 60, 1: 25, 2: 36, 3: 98}` | Cluster 1 shrinks to 25 bowlers. |
| **5** | 0.2318 | 1.1717 | 84.06 | 425.86 | 11 | 73 | 0.1507 | `{0: 62, 1: 73, 2: 57, 3: 11, 4: 16}` | Fragmented. |
| **6** | 0.2132 | 1.2307 | 78.61 | 384.85 | 9 | 72 | 0.1250 | `{0: 36, 1: 39, 2: 46, 3: 72, 4: 9, 5: 17}` | Severe fragmentation. |
| **7** | 0.2130 | 1.1772 | 76.70 | 345.36 | 9 | 63 | 0.1429 | `{0: 35, 1: 36, 2: 40, 3: 63, 4: 13, 5: 23, 6: 9}` | Severe fragmentation. |
| **8** | 0.2055 | 1.1926 | 73.80 | 317.53 | 9 | 59 | 0.1525 | `{0: 9, 1: 43, 2: 59, 3: 10, 4: 25, 5: 29, 6: 35, 7: 9}` | Severe noise fitting. |

**Rationale for Bowling $K=3$ & Mathematical Trade-Off**:
We explicitly document that $K=2$ is the mathematical champion under silhouette score ($0.2976$ vs $0.2263$). However, $K=2$ is a blunt binary partition that simply splits bowlers into expensive ($> 10.9$ RPO) and non-expensive ($< 8.7$ RPO), combining elite run controllers with ordinary containing options. $K=3$ provides immense practical scouting value by isolating **Economical Pressure Controllers** ($N=62$, Econ 7.97 RPO, Bnd/100 15.2) from **Moderate-Containment Bowlers** ($N=109$) and **Pressure-Vulnerable Bowlers** ($N=48$). It maintains healthy cluster sizes (all $\ge 48$, balance ratio $0.4404$) without micro-cluster collapse.

### 5.3 Multi-Seed Stability Analysis
Clustering partition stability was evaluated across 5 random seeds (`[42, 100, 2024, 7, 999]`) using Adjusted Rand Index (ARI):
- **Batting $K=3$ Stability**: $\text{Mean ARI} = \mathbf{1.0000}$ (100% identical partition across all seeds).
- **Bowling $K=3$ Stability**: $\text{Mean ARI} = \mathbf{0.9404}$ (high structural stability across all seeds).

---

## 6. Archetype Taxonomy & Corrected Profiles

### 6.1 Batting Archetypes ($K = 3$)

```
+----------------------------------------------------------------------------------------------------+
|                                    BATTING ARCHETYPES (K=3)                                       |
+----------------------------------------------------------------------------------------------------+
|  Cluster 0: Pressure-Struggling / Low-Tempo Batters (N=45 Primary, 314 Emerging)                   |
|  - Pressure SR: 111.67 (Median: 118.18) | Delta SR: -11.72 (Median: -9.40)                         |
|  - Dot%: 42.96% (Median: 41.79%)        | Boundary%: 13.51% (Median: 13.08%)                       |
|  - Batting Avg: 10.63 (Median: 9.75)    | Mean Clutch IQ: 39.04                                    |
|  - Reps: Shaheen Afridi, Keshav Maharaj, Rahul Chahar, Shoriful Islam, Harshit Rana                |
+----------------------------------------------------------------------------------------------------+
|  Cluster 1: Explosive Pressure Finishers & Boundary Hitters (N=96 Primary, 73 Emerging)           |
|  - Pressure SR: 182.72 (Median: 180.61) | Delta SR: +51.13 (Median: +47.07)                        |
|  - Dot%: 25.73% (Median: 26.09%)        | Boundary%: 25.98% (Median: 25.99%)                       |
|  - Batting Avg: 32.40 (Median: 28.89)   | Mean Clutch IQ: 80.41                                    |
|  - Reps: Tristan Stubbs, MS Dhoni, Tim David, Najibullah Zadran, Sikandar Raza, Heinrich Klaasen   |
+----------------------------------------------------------------------------------------------------+
|  Cluster 2: Steady Pressure Anchors & Strike Rotators (N=108 Primary, 139 Emerging)                |
|  - Pressure SR: 149.20 (Median: 148.90) | Delta SR: +23.46 (Median: +23.54)                        |
|  - Dot%: 30.14% (Median: 30.13%)        | Boundary%: 19.09% (Median: 19.09%)                       |
|  - Batting Avg: 20.14 (Median: 17.78)   | Mean Clutch IQ: 65.32                                    |
|  - Reps: Clive Madande, Mark Adair, Karim Janat, Wellington Masakadza, Jason Holder, Hardik Pandya|
+----------------------------------------------------------------------------------------------------+
```

#### Detailed Centroid Metrics (Unscaled Primary Cohort):
| Metric | Cluster 0: Struggling Batters | Cluster 1: Explosive Finishers | Cluster 2: Steady Anchors |
|---|:---:|:---:|:---:|
| **Primary Count ($N_{\ge 50}$)** | 45 | 96 | 108 |
| **Emerging Count ($N_{< 50}$)** | 314 | 73 | 139 |
| **Total Player Count** | 359 | 169 | 247 |
| **Pressure Strike Rate (Mean / Med)** | 111.67 / 118.18 | **182.72 / 180.61** | 149.20 / 148.90 |
| **Raw Delta Strike Rate (Mean / Med)** | -11.72 / -9.40 | **+51.13 / +47.07** | +23.46 / +23.54 |
| **Pressure Dot Ball % (Mean / Med)** | 42.96% / 41.79% | **25.73% / 26.09%** | 30.14% / 30.13% |
| **Pressure Boundary Ball % (Mean / Med)** | 13.51% / 13.08% | **25.98% / 25.99%** | 19.09% / 19.09% |
| **Batting Average Imputed (Mean / Med)** | 10.63 / 9.75 | **32.40 / 28.89** | 20.14 / 17.78 |
| **Mean Balls Faced / Matches** | 98.4 balls / 10.5 matches | 268.2 balls / 24.1 matches | 179.3 balls / 18.2 matches |
| **Mean Clutch IQ Score** | 39.04 | **80.41** | 65.32 |

---

### 6.2 Bowling Archetypes ($K = 3$)

```
+----------------------------------------------------------------------------------------------------+
|                                    BOWLING ARCHETYPES (K=3)                                       |
+----------------------------------------------------------------------------------------------------+
|  Cluster 0: Economical Pressure Controllers (N=62 Primary, 108 Emerging)                           |
|  - Pressure Economy: 7.97 RPO (Median: 8.32) | Delta Economy: -0.05 RPO (Median: -0.09)            |
|  - Wickets/100 Balls: 8.25 (Median: 8.37)    | Dot%: 38.24% (Median: 37.38%)                       |
|  - Boundary Balls/100: 15.24 (Median: 16.15) | Mean Clutch IQ: 54.49                               |
|  - Reps: Sunil Narine, Pramod Madushan, Rasikh Salam, Abrar Ahmed, Mohammad Nawaz, Abdul Saqlain   |
+----------------------------------------------------------------------------------------------------+
|  Cluster 1: Moderate-Containment / Mid-Tier Pressure Bowlers (N=109 Primary, 66 Emerging)         |
|  - Pressure Economy: 9.97 RPO (Median: 9.97) | Delta Economy: -1.39 RPO (Median: -1.41)            |
|  - Wickets/100 Balls: 7.61 (Median: 7.42)    | Dot%: 32.48% (Median: 32.22%)                       |
|  - Boundary Balls/100: 21.52 (Median: 21.49) | Mean Clutch IQ: 40.30                               |
|  - Reps: Arshdeep Singh, Mohammed Siraj, Odean Smith, Lizaad Williams, Xavier Bartlett             |
+----------------------------------------------------------------------------------------------------+
|  Cluster 2: Pressure-Vulnerable / High-Concession Bowlers (N=48 Primary, 150 Emerging)             |
|  - Pressure Economy: 11.68 RPO (Median: 11.45)| Delta Economy: -3.23 RPO (Median: -2.98)           |
|  - Wickets/100 Balls: 6.38 (Median: 6.58)    | Dot%: 27.73% (Median: 27.78%)                       |
|  - Boundary Balls/100: 27.12 (Median: 26.53) | Mean Clutch IQ: 26.06                               |
|  - Reps: Tushar Deshpande, Mukesh Kumar, Patrick Cummins, Mohammed Shami, Khaleel Ahmed            |
+----------------------------------------------------------------------------------------------------+
```

#### Detailed Centroid Metrics (Unscaled Primary Cohort):
| Metric | Cluster 0: Controllers | Cluster 1: Mid-Tier Bowlers | Cluster 2: Vulnerable Bowlers |
|---|:---:|:---:|:---:|
| **Primary Count ($N_{\ge 50}$)** | 62 | 109 | 48 |
| **Emerging Count ($N_{< 50}$)** | 108 | 66 | 150 |
| **Total Player Count** | 170 | 175 | 198 |
| **Pressure Economy (Mean / Med)** | **7.97 / 8.32** | 9.97 / 9.97 | 11.68 / 11.45 |
| **Raw Delta Economy (Mean / Med)** | **-0.05 / -0.09** | -1.39 / -1.41 | -3.23 / -2.98 |
| **Wickets / 100 Balls (Mean / Med)** | **8.25 / 8.37** | 7.61 / 7.42 | 6.38 / 6.58 |
| **Pressure Dot Ball % (Mean / Med)** | **38.24% / 37.38%** | 32.48% / 32.22% | 27.73% / 27.78% |
| **Boundary Balls / 100 (Mean / Med)** | **15.24% / 16.15%** | 21.52% / 21.49% | 27.12% / 26.53% |
| **Mean Legal Balls / Matches** | 212.4 balls / 17.5 matches | 258.9 balls / 20.8 matches | 205.1 balls / 16.9 matches |
| **Mean Clutch IQ Score** | **54.49** | 40.30 | 26.06 |

---

## 7. Decoupled Validation via Clutch IQ

Clutch IQ, rank, and Top 10 status were strictly withheld during feature engineering and model training:
$$\text{Clutch IQ} \notin \mathcal{F}_{\text{model}}$$

Comparing the mean and median Clutch IQ across the discovered clusters provides an objective external sanity check:
- **Batters**:
  - Cluster 1 (Explosive Finishers): Mean Clutch IQ = **80.41** (Highest)
  - Cluster 2 (Steady Anchors): Mean Clutch IQ = **65.32**
  - Cluster 0 (Struggling Batters): Mean Clutch IQ = **39.04** (Lowest)
- **Bowlers**:
  - Cluster 0 (Economical Controllers): Mean Clutch IQ = **54.49** (Highest)
  - Cluster 1 (Mid-Tier Bowlers): Mean Clutch IQ = **40.30**
  - Cluster 2 (Pressure-Vulnerable): Mean Clutch IQ = **26.06** (Lowest)

This monotonic alignment proves that the unsupervised geometry captures genuine cricket capability while preserving strict statistical independence. Cluster membership describes *style and behavioral profile*, while Clutch IQ measures *magnitude of pressure elevation*.

---

## 8. Known Limitations & Scope Boundaries

1. **Phase-Agnostic Pressure Definition**: The underlying features aggregate all deliveries meeting the approved Phase 2 pressure definition (death overs 16–20 and close chases with RRR $\ge 9.0$). They do NOT evaluate powerplay performance or specific individual overs (e.g. over 16 vs over 19). All tactical roles are presented as candidate scouting hypotheses.
2. **Emerging Cohort Volatility**: Provisional cluster assignments for emerging players ($< 50$ balls) are based on small samples. While projecting them via the frozen pipeline prevents centroid distortion, their individual assignments carry higher variance and must be treated as indicative rather than established.

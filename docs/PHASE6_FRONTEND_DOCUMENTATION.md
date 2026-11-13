# SUPER RR — CLUTCH IQ: Frontend Documentation & UI/UX Architecture

**Project:** SUPER RR — CLUTCH IQ: Beyond Statistics. Discovering Players Who Perform Under Pressure.  
**Phase:** Phase 6 — Complete React Frontend Development  
**Version:** 1.0.0 (Production Ready)  
**Date:** November 2026  
**License:** Proprietary / Rajasthan Royals Hackathon Submission  

---

## 1. Executive Overview

The **SUPER RR — CLUTCH IQ** frontend is a high-performance, responsive single-page web application designed for cricket scouts, performance analysts, team management, and cricket enthusiasts. It translates deep econometric Bayesian shrinkage ratings, unsupervised K-Means archetypal profiles, and fine-grained situational pressure metrics into an intuitive, visually stunning sports analytics product.

The design philosophy rejects generic boilerplate dashboard templates in favor of a bespoke visual identity rooted in the **Rajasthan Royals** brand palette:
- **Deep Graphite (`#1C1D20`)**: Deep obsidian base surface providing superior contrast.
- **Soft Cloud White (`#F2F4F1`)**: High-legibility text and crisp structural elements.
- **Sunshine Yellow (`#FFC928`)**: Vibrant accent color representing moments of clutch brilliance, energy, and royal pride.
- **Subtle Glassmorphism**: Translucent floating cards (`rgba(242, 244, 241, 0.045)`), frosted backdrop blurs (`backdrop-blur-md`), and glowing border highlights.

---

## 2. Technical Stack & Dependencies

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Core Framework** | React | `^18.3.1` | Component-driven UI architecture, Concurrent Mode |
| **DOM Engine** | React DOM | `^18.3.1` | Client-side DOM rendering |
| **Build & Bundler** | Vite | `^5.4.21` | Sub-second HMR, optimized Rollup bundling |
| **Routing** | React Router DOM | `^6.28.0` | Declarative client-side routing, URL state synchronization |
| **Styling** | Tailwind CSS | `^3.4.14` | Utility-first CSS, custom design tokens, dark theme |
| **Post-Processing**| PostCSS & Autoprefixer | `^8.4.47` / `^10.4.20` | Cross-browser CSS compatibility |
| **Data Visualization** | Recharts | `^2.12.7` | Declarative SVG charting (Bar, Radar, Line, Scatter) |
| **Micro-Interactions** | Framer Motion | `^11.11.11` | Smooth spring transitions, card hover elevation |
| **Icons** | Lucide React | `^0.454.0` | Accessible, clean stroke icons |
| **Utility** | clsx & tailwind-merge | `^2.1.1` / `^2.5.4` | Conflict-free conditional CSS class composition |

---

## 3. Directory Structure

```text
frontend/
├── dist/                          # Production build output
│   ├── assets/
│   │   ├── index-*.css            # Minified stylesheet (28.17 kB)
│   │   ├── index-*.js             # Main application bundle (115.87 kB)
│   │   ├── vendor-react-*.js      # React runtime bundle (162.83 kB)
│   │   ├── vendor-charts-*.js     # Recharts charting library (377.67 kB)
│   │   ├── vendor-icons-*.js      # Lucide SVG icons (12.34 kB)
│   │   └── vendor-anim-*.js       # Framer Motion animation engine (0.93 kB)
│   └── index.html                 # Minified entry point
├── node_modules/                  # Package dependencies
├── public/                        # Static static assets
├── src/
│   ├── components/                # Reusable UI component library
│   │   ├── ClutchBadge.jsx        # Sunshine Yellow clutch score indicator & pill
│   │   ├── ErrorMessage.jsx       # Graceful network error & retry component
│   │   ├── Footer.jsx             # Brand footer with live API connection indicator
│   │   ├── GlassCard.jsx          # Frosted glass panel with hover physics
│   │   ├── LoadingSkeleton.jsx    # Shimmering card, table, and stat skeletons
│   │   └── Navbar.jsx             # Responsive glassmorphic sticky top navbar
│   ├── pages/                     # Full-page feature views
│   │   ├── ArchetypesPage.jsx     # ML Archetypes Studio (K-Means 6 Archetypes)
│   │   ├── DashboardPage.jsx      # Macro overview & Quick Tournament Dashboard
│   │   ├── LandingPage.jsx        # Premium hero landing & conceptual introduction
│   │   ├── LeaderboardsPage.jsx   # Filterable Clutch IQ rankings (Batting/Bowling)
│   │   ├── MethodologyPage.jsx    # Complete whitepaper & mathematical formulas
│   │   ├── PlayerComparisonPage.jsx# Head-to-head multi-player radar & bar comparator
│   │   ├── PlayerDetailPage.jsx   # Deep-dive individual player scouting profile
│   │   ├── PlayerExplorerPage.jsx # Global 1,217-player search & role directory
│   │   └── PressureAnalyticsPage.jsx# 8 Situational pressure segments explorer
│   ├── services/
│   │   └── api.js                 # Unified Axios/Fetch API client with error handling
│   ├── App.jsx                    # Root routing container & ambient background lighting
│   ├── index.css                  # Custom Tailwind styles, scrollbars, glass utility
│   └── main.jsx                   # React 18 bootstrap mount
├── index.html                     # HTML5 shell with Google Inter & Manrope fonts
├── package.json                   # Project manifest & build scripts
├── postcss.config.js              # PostCSS plugin registration
├── tailwind.config.js             # Custom colors, typography, and shadow tokens
└── vite.config.js                 # Vite build settings & Rollup manual vendor chunking
```

---

## 4. Design System Specification

### 4.1 Color Palette

```css
/* Deep Graphite Surfaces */
--color-graphite-950: #141517;
--color-graphite-900: #1C1D20; /* Primary Background */
--color-graphite-850: #212226;
--color-graphite-800: #25262A; /* Card Surface */
--color-graphite-700: #2B2C30; /* Elevated Surface / Input */
--color-graphite-600: #3A3B40; /* Active Border */

/* Soft Cloud Typography */
--color-cloud-100: #F2F4F1;   /* Headings & High Contrast Text */
--color-cloud-200: #D8DBD6;   /* Body Text */
--color-cloud-300: #A6A9A5;   /* Secondary / Muted Text */
--color-cloud-400: #717370;   /* Subtle Badges / Placeholder */

/* Sunshine Yellow Accents */
--color-sunshine-300: #FFE17D; /* Hover Highlights */
--color-sunshine-400: #FFD554; /* Light Accent */
--color-sunshine-500: #FFC928; /* Primary Brand Gold / Sunshine */
--color-sunshine-600: #E6B015; /* Active Press */
--color-sunshine-700: #B88905; /* Deep Accent */
```

### 4.2 Glassmorphism Utility Tokens

- `.glass-panel`: `bg-[#F2F4F1]/[0.045] backdrop-blur-md border border-[#F2F4F1]/10 rounded-2xl`
- `.glass-panel-elevated`: `bg-[#F2F4F1]/[0.08] backdrop-blur-lg border border-[#F2F4F1]/20 shadow-2xl`
- `.sunshine-glow`: `box-shadow: 0 0 25px -5px rgba(255, 201, 40, 0.35)`

---

## 5. API Integration Layer (`services/api.js`)

The frontend interacts with the FastAPI backend through a typed, centralized API service module. All endpoints use standard query string serialization and error trapping.

```javascript
// Base configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Supported API modules:
- fetchHealth()
- fetchSummary()
- fetchLeaderboard({ discipline, cohort, min_balls, sort_by, order, limit, offset })
- fetchTop10({ discipline, cohort })
- fetchPlayer(id)
- fetchPlayers({ search, role, cohort, limit, offset })
- comparePlayers(ids)
- fetchArchetypes({ discipline })
- fetchArchetype(clusterId)
- fetchPressureSegments()
- fetchPressureComparison({ discipline, player_id })
```

---

## 6. Detailed Feature & Page Walkthrough

### 6.1 Landing Page (`/`)
- **Hero Statement:** *"BEYOND STATISTICS. DISCOVERING PLAYERS WHO PERFORM UNDER PRESSURE."*
- **Live Counter Grid:** Fetches backend `/summary` to showcase 1,217 players, 200,961 deliveries, 26.6% pressure volume, and 6 ML archetypes.
- **Conceptual Explainer:** Visual breakdown of the fundamental thesis—why aggregate T20 stats deceive and why Bayesian regularized pressure deltas matter.
- **Top Performers Spotlight:** Dynamic carousel/preview of #1 clutch batter (David Miller) and #1 clutch bowler (Sunil Narine).
- **Interactive Call-to-Actions:** Direct links to Dashboard, Leaderboards, Archetypes, and Methodology.

### 6.2 Overview Dashboard (`/dashboard`)
- **Tournament Macro Stats:** Quick cards for Pressure Runs, Pressure Wickets, Pressure Ball Percentage, and Total Tracked Matches.
- **Quick Player Search:** Live debounced autocomplete jumper allowing rapid navigation to any player's dossier.
- **Top 5 Clutch Batters & Bowlers:** Side-by-side leaderboard podium featuring Clutch IQ badges, average delta, and archetype tag.
- **Archetype Radar / Distribution:** Visual breakdown of how the tournament's talent pool divides into the 6 clusters.
- **Comparison Jump-off:** Quick button to launch multi-player comparison.

### 6.3 Clutch IQ Leaderboards (`/leaderboards`)
- **Discipline Toggle:** Instant tabbed switching between Batting (775 players) and Bowling (543 players).
- **Cohort Segmenter:** Filter by **Primary Cohort** ($\ge 120$ balls / $\ge 90$ pressure balls) or **Emerging Cohort** ($30-119$ balls faced / $24-89$ balls bowled).
- **Interactive Sorting:** Sort by Rank, Clutch IQ Score, Balls Faced/Bowled, Pressure Average, Pressure Strike Rate/Economy, and Raw Delta.
- **Min Balls Slider:** Client-side filter slider to customize minimum experience threshold.
- **Pagination & Deep Linking:** 20 players per page with direct routing to `/players/:id`.

### 6.4 Player Explorer (`/players`)
- **Full Catalog Search:** Search across all 1,217 registered players by name or ID.
- **Role Filtering:** Filter by All Players, Pure Batters, Pure Bowlers, or All-Rounders.
- **Cohort Filtering:** Toggle Primary or Emerging tiers.
- **Dual Clutch IQ Badges:** Displays both Batting Clutch IQ and Bowling Clutch IQ where available, highlighting true all-round impact.

### 6.5 Player Detail Profile (`/players/:id`)
- **Header Dossier:** Player name, unique ID, primary archetype badge, dual Clutch IQ scores.
- **Pressure vs. Baseline Metric Matrix:**
  - Batting: Average, Strike Rate, Dot-Ball %, Boundary %, Balls per Dismissal.
  - Bowling: Average, Economy Rate, Strike Rate, Dot-Ball %, Boundary Conceded %.
- **Bayesian Regularization Card:** Exposes raw sample size $N_i$, prior parameter $M$, shrinkage weight $w_i$, and prior mean $\mu_0$, showing exactly why the player's score was moderated.
- **Archetype Scouting Assessment:** Centroid comparison, key strengths, potential weaknesses, and tactical scouting advice.
- **Unavailable Role Guard:** Gracefully handles players who never bowled or never batted with informative context cards.

### 6.6 Player Comparison Studio (`/compare`)
- **Multi-Player Head-to-Head:** Compare 2 to 5 players simultaneously.
- **Live Search & Chip Management:** Search and add any player from the database; remove with one click.
- **Interactive Recharts Bar Comparison:** Visualizes Clutch IQ Score, Pressure Strike Rate/Economy, and Pressure Average.
- **Side-by-Side Detailed Matrix:** Full tabular breakdown of all pressure and baseline metrics across all selected players.

### 6.7 ML Archetypes Studio (`/archetypes`)
- **Dual Discipline Tabs:** Batting Archetypes (Anchor Stabilizers, Volatile Finishers, Balanced Accumulators) vs Bowling Archetypes (Death Specialists, Defensive Controllers, Volume Strike Bowlers).
- **Cluster Centroids & Feature Cards:** Visual display of the normalized feature coordinates ($z$-scores) that define the cluster.
- **Scouting Narratives:** Actionable tactical advice on how IPL franchises should utilize each archetype in auction and game strategy.
- **Interactive Roster Viewer:** Filterable list of all players assigned to the selected archetype with pagination.

### 6.8 Pressure Situations Engine (`/analytics`)
- **The 8 Pressure Segments:** Comprehensive cards detailing Death Overs (16–20), Run Chase Pressure ($RRR > 9.0$), Close Finishes (margin $\le 12$ runs / 12 balls), Top-Order Collapse ($\le 30/3$), Knockouts, High-Leverage, Death $\times$ Knockout, and Run Chase $\times$ Knockout.
- **Volume & Delivery Distribution:** Visual bar charts showing ball counts and percentages for each segment.
- **Strike Rate vs Economy Impact:** Comparison of how scoring efficiency swings between normal situations and high-leverage situations.
- **Set Algebra Verification:** Interactive card verifying that High Pressure ($53,453$ balls) and Normal Pressure ($147,508$ balls) sum exactly to the full tournament delivery count of $200,961$ balls.

### 6.9 Methodology & Whitepaper (`/methodology`)
- **Foundational Formula Documentation:** Complete mathematical equations for batting pressure score, bowling pressure score, and Bayesian empirical shrinkage.
- **Mathematical Integrity Proofs:** Explains shrinkage weight $w_i = \frac{N_i}{N_i + M}$ with $M=120$ (batting) and $M=90$ (bowling).
- **Clustering Validation:** Documents PCA variance explained ($>70\%$) and silhouette validation for $K=3$.
- **Known Limitations:** Honest sports science disclosure regarding opposition bowler strength, pitch degradation, and historical data sparsity.

---

## 7. Performance & Build Verification

- **Production Build:** Vite 5.4 + Rollup WASM pipeline compiles in under 15 seconds.
- **Zero Bundle Warnings:** Manual chunking splits vendor libraries into separate cached bundles:
  - React/DOM/Router: 162 kB
  - Recharts: 377 kB
  - Application Code: 115 kB
  - CSS: 28 kB
- **Sub-50ms API Roundtrips:** FastAPI backend in-memory cache delivers instant transitions across all routes.

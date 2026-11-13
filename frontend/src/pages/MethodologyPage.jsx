import React from 'react';
import { 
  BookOpen, 
  Target, 
  TrendingUp, 
  ShieldCheck, 
  Layers, 
  AlertCircle, 
  CheckCircle, 
  Scale,
  Sparkles
} from 'lucide-react';
import GlassCard from '../components/GlassCard';

export default function MethodologyPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      {/* 1. Header */}
      <div className="text-center space-y-3 pb-8 border-b border-white/10">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs font-bold text-[#FFC928] font-display">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Transparent Mathematical Framework</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-black font-display text-[#F2F4F1] uppercase tracking-tight">
          RESEARCH & METHODOLOGY
        </h1>
        <p className="text-xs sm:text-sm text-[#A6A9A5] max-w-2xl mx-auto leading-relaxed">
          The principles, empirical formulas, Bayesian credibility shrinkage, and machine learning models behind SUPER RR — CLUTCH IQ.
        </p>
      </div>

      {/* 2. The Core Philosophy */}
      <section className="space-y-4">
        <h2 className="text-xl sm:text-2xl font-black font-display text-[#F2F4F1] uppercase flex items-center space-x-2">
          <Target className="w-5 h-5 text-[#FFC928]" />
          <span>1. The Core Philosophy of Clutch IQ</span>
        </h2>
        <GlassCard className="p-6 space-y-3" hover={false}>
          <p className="text-xs sm:text-sm text-[#F2F4F1] leading-relaxed">
            In standard cricket analytics, traditional averages and strike rates aggregate all match deliveries together. A boundary hit in the 3rd over of a dead group stage match is treated identically to a boundary hit with 12 runs required off 4 balls in an IPL Playoff.
          </p>
          <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
            <strong className="text-[#FFC928]">CLUTCH IQ</strong> introduces three critical mathematical innovations:
          </p>
          <ul className="list-disc pl-5 space-y-1 text-xs text-[#A6A9A5]">
            <li><strong>Situational Pressure Isolation:</strong> Filtering deliveries based on in-match pressure context without outcome leakage.</li>
            <li><strong>Personal Baseline Elevation:</strong> Evaluating whether a player exceeds their own baseline standards when the match tightens.</li>
            <li><strong>Empirical Bayes Credibility Shrinkage:</strong> Penalizing low-sample flukes so small-sample anomalies cannot artificially top the rankings.</li>
          </ul>
        </GlassCard>
      </section>

      {/* 3. Defining Pressure Situations */}
      <section className="space-y-4">
        <h2 className="text-xl sm:text-2xl font-black font-display text-[#F2F4F1] uppercase flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-[#FFC928]" />
          <span>2. Situational Pressure Definition & Zero Leakage</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <GlassCard className="p-5 space-y-2" hover={false}>
            <span className="text-xs font-bold text-[#FFC928] uppercase font-display">1. Death Overs</span>
            <p className="text-xs text-[#A6A9A5] leading-relaxed">
              Overs 16–20 (Deliveries 15.1 to 19.6). In Phase 0 and Phase 1 audit, Death Overs account for 44,792 regular deliveries where fielding restrictions tighten and scoring demand peaks.
            </p>
          </GlassCard>

          <GlassCard className="p-5 space-y-2" hover={false}>
            <span className="text-xs font-bold text-[#FFC928] uppercase font-display">2. Close Chases</span>
            <p className="text-xs text-[#A6A9A5] leading-relaxed">
              Second innings only, with 36 or fewer legal balls remaining and a Required Run Rate (RRR) $\ge 9.00$ runs per over. Represents 8,604 critical match-deciding deliveries.
            </p>
          </GlassCard>

          <GlassCard className="p-5 space-y-2" hover={false}>
            <span className="text-xs font-bold text-[#FFC928] uppercase font-display">3. Knockout Fixtures</span>
            <p className="text-xs text-[#A6A9A5] leading-relaxed">
              Eliminator, Qualifier, Semi-Final, and Final matches where tournament elimination is at stake. Accounts for 10,724 deliveries across championship deciders.
            </p>
          </GlassCard>
        </div>

        <GlassCard className="p-4 bg-emerald-500/5 border-emerald-500/20 text-xs text-[#A6A9A5] flex items-start space-x-3" hover={false}>
          <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <p>
            <strong className="text-emerald-400">Zero Outcome Leakage Guarantee:</strong> Final match margins (e.g. winning by $\le 15$ runs) are never used retrospectively to classify early overs as pressure deliveries. Classification is strictly determined by game state at the instant the ball is bowled.
          </p>
        </GlassCard>
      </section>

      {/* 4. Mathematical Formulas */}
      <section className="space-y-4">
        <h2 className="text-xl sm:text-2xl font-black font-display text-[#F2F4F1] uppercase flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-[#FFC928]" />
          <span>3. Mathematical Formulas</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Batting Formulas */}
          <GlassCard className="p-6 space-y-4" hover={false}>
            <h3 className="text-base font-bold text-[#FFC928] font-display uppercase tracking-wider">
              Batting Clutch IQ Formulation
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[#A6A9A5] block mb-1">1. Regularized Baseline Strike Rate:</span>
                <code className="block p-2.5 rounded-lg bg-black/40 text-[#F2F4F1] font-mono text-[11px]">
                  SR_reg_base = (Runs_base + 100 * 1.30) / (Balls_base + 100) * 100
                </code>
              </div>

              <div>
                <span className="text-[#A6A9A5] block mb-1">2. Raw Delta Strike Rate:</span>
                <code className="block p-2.5 rounded-lg bg-black/40 text-[#F2F4F1] font-mono text-[11px]">
                  ΔSR = SR_pressure - SR_reg_base
                </code>
              </div>

              <div>
                <span className="text-[#A6A9A5] block mb-1">3. Empirical Bayes Reliability Weight:</span>
                <code className="block p-2.5 rounded-lg bg-black/40 text-[#F2F4F1] font-mono text-[11px]">
                  w_i = n_balls / (n_balls + 150)
                </code>
              </div>

              <div>
                <span className="text-[#A6A9A5] block mb-1">4. Credibility-Shrunk Score:</span>
                <code className="block p-2.5 rounded-lg bg-black/40 text-[#FFC928] font-mono text-[11px]">
                  Clutch_IQ = Scale(w_i * ΔSR, bounds=[0, 100])
                </code>
              </div>
            </div>
          </GlassCard>

          {/* Bowling Formulas */}
          <GlassCard className="p-6 space-y-4" hover={false}>
            <h3 className="text-base font-bold text-[#FFC928] font-display uppercase tracking-wider">
              Bowling Clutch IQ Formulation
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[#A6A9A5] block mb-1">1. Regularized Baseline Economy:</span>
                <code className="block p-2.5 rounded-lg bg-black/40 text-[#F2F4F1] font-mono text-[11px]">
                  Econ_reg_base = (Runs_base + 60 * 1.30) / ((Balls_base + 60) / 6)
                </code>
              </div>

              <div>
                <span className="text-[#A6A9A5] block mb-1">2. Raw Delta Economy (Inverted for Run Saving):</span>
                <code className="block p-2.5 rounded-lg bg-black/40 text-[#F2F4F1] font-mono text-[11px]">
                  ΔEcon = Econ_reg_base - Econ_pressure
                </code>
              </div>

              <div>
                <span className="text-[#A6A9A5] block mb-1">3. Empirical Bayes Reliability Weight:</span>
                <code className="block p-2.5 rounded-lg bg-black/40 text-[#F2F4F1] font-mono text-[11px]">
                  w_i = n_legal_balls / (n_legal_balls + 120)
                </code>
              </div>

              <div>
                <span className="text-[#A6A9A5] block mb-1">4. Credibility-Shrunk Score:</span>
                <code className="block p-2.5 rounded-lg bg-black/40 text-[#FFC928] font-mono text-[11px]">
                  Clutch_IQ = Scale(w_i * ΔEcon, bounds=[0, 100])
                </code>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* 5. Cohort Separation & Minimum Sample Sizes */}
      <section className="space-y-4">
        <h2 className="text-xl sm:text-2xl font-black font-display text-[#F2F4F1] uppercase flex items-center space-x-2">
          <Scale className="w-5 h-5 text-[#FFC928]" />
          <span>4. Minimum Sample Sizes & Cohort Separation</span>
        </h2>
        <GlassCard className="p-6 space-y-3" hover={false}>
          <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
            To prevent statistical artifacts from polluting scouting leaderboards, players are partitioned into two distinct cohorts:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1">
              <span className="text-xs font-bold text-[#F2F4F1] uppercase font-display">Primary Cohort (&ge; 50 Pressure Balls)</span>
              <p className="text-xs text-[#A6A9A5]">
                249 Batters and 219 Bowlers. Eligible for primary rankings (#1 through #249 / #219). Highly reliable sample sizes across multiple match situations.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-1">
              <span className="text-xs font-bold text-amber-300 uppercase font-display">Emerging Cohort (&lt; 50 Pressure Balls)</span>
              <p className="text-xs text-[#A6A9A5]">
                526 Batters and 324 Bowlers. Shrunk heavily toward population medians to prevent sample flukes. Displayed as emerging performers without unearned high ranks.
              </p>
            </div>
          </div>
        </GlassCard>
      </section>

      {/* 6. Unsupervised Machine Learning */}
      <section className="space-y-4">
        <h2 className="text-xl sm:text-2xl font-black font-display text-[#F2F4F1] uppercase flex items-center space-x-2">
          <Layers className="w-5 h-5 text-[#FFC928]" />
          <span>5. Machine Learning Archetypes (K-Means, K=3)</span>
        </h2>
        <GlassCard className="p-6 space-y-3" hover={false}>
          <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
            Following rigorous multicollinearity testing in Phase 4, exact algebraic redundancies were eliminated, reducing feature space condition numbers from $10^{16}$ to $151.95$ (batting) and $105.22$ (bowling). Optimal cluster count $K=3$ was validated using Silhouette Coefficient analysis ($0.3070$ for batting, $0.2263$ for bowling) and cluster balance ratios ($&gt; 0.40$).
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
            <div className="p-3 rounded-xl bg-black/20 border border-white/5">
              <span className="font-bold text-[#FFC928] block mb-1">Batting Clustering Features:</span>
              <span className="text-[#A6A9A5]">Pressure Strike Rate, Pressure Batting Average (median-imputed for 0-dismissals), Boundary Ball %, Dot Ball %, Raw Delta SR.</span>
            </div>
            <div className="p-3 rounded-xl bg-black/20 border border-white/5">
              <span className="font-bold text-[#FFC928] block mb-1">Bowling Clustering Features:</span>
              <span className="text-[#A6A9A5]">Pressure Economy Rate, Wickets per Legal Ball (continuous rate), Boundary Balls Conceded per 100 Balls, Dot Ball %, Raw Delta Economy.</span>
            </div>
          </div>
        </GlassCard>
      </section>

      {/* 7. Known Dataset Limitations */}
      <section className="space-y-4">
        <h2 className="text-xl sm:text-2xl font-black font-display text-[#F2F4F1] uppercase flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 text-[#FFC928]" />
          <span>6. Known Limitations & Caveats</span>
        </h2>
        <GlassCard className="p-6 space-y-2 text-xs text-[#A6A9A5] leading-relaxed" hover={false}>
          <p>• <strong>Tournament Sample:</strong> Covers 883 T20 matches across 14 competitions from 2021 to 2024. Does not include domestic franchise tournaments outside the audited dataset.</p>
          <p>• <strong>Super Over Isolation:</strong> In accordance with ICC Playing Condition Rule 16, the 38 Super Over deliveries across 6 matches are strictly quarantined and not added to 20-over rate statistics.</p>
          <p>• <strong>Archetypes Are Not Rank Quality:</strong> A player belonging to the "Anchor Accumulator" cluster can possess an elite Clutch IQ if their tactical anchor role elevated their team above baseline.</p>
        </GlassCard>
      </section>
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Flame, 
  Trophy, 
  Target, 
  Zap, 
  ArrowRight, 
  ShieldCheck, 
  Activity, 
  Sparkles, 
  Layers, 
  TrendingUp, 
  Search,
  ExternalLink
} from 'lucide-react';
import api from '../services/api';
import ClutchBadge from '../components/ClutchBadge';
import GlassCard from '../components/GlassCard';

export default function LandingPage() {
  const [metadata, setMetadata] = useState(null);
  const [topBatters, setTopBatters] = useState([]);
  const [topBowlers, setTopBowlers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [metaData, batData, bowlData] = await Promise.all([
          api.getMetadata().catch(() => null),
          api.getBattersLeaderboard({ page: 1, page_size: 3, cohort: 'primary' }).catch(() => ({ items: [] })),
          api.getBowlersLeaderboard({ page: 1, page_size: 3, cohort: 'primary' }).catch(() => ({ items: [] })),
        ]);
        setMetadata(metaData);
        setTopBatters(batData.items || []);
        setTopBowlers(bowlData.items || []);
      } catch (err) {
        console.error('Error loading landing page data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="relative overflow-hidden space-y-24">
      {/* Background radial sunshine glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-[#FFC928]/10 rounded-full blur-[140px] pointer-events-none -z-10" />

      {/* 1. HERO SECTION */}
      <section className="relative pt-12 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
        {/* Subtle Pill Tag */}
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-md">
          <Sparkles className="w-4 h-4 text-[#FFC928]" />
          <span className="text-xs uppercase tracking-widest text-[#FFC928] font-bold font-display">
            Rajasthan Royals Hackathon 2026
          </span>
          <span className="text-xs text-[#A6A9A5]">• Empirical Cricket Intelligence</span>
        </div>

        {/* Main Editorial Hero Headline */}
        <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black font-display tracking-tight text-[#F2F4F1] max-w-5xl mx-auto uppercase leading-[0.95]">
          BEYOND <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FFC928] via-[#FFE27B] to-[#FFC928] sunshine-text-glow">STATISTICS.</span>
        </h1>

        <p className="mt-6 text-xl sm:text-2xl font-semibold text-[#F2F4F1] max-w-3xl mx-auto font-display">
          Discovering Players Who Perform Under Pressure.
        </p>

        <p className="mt-4 text-sm sm:text-base text-[#A6A9A5] max-w-2xl mx-auto leading-relaxed">
          Every player has numbers. Champions reveal themselves when the pressure rises. 
          Discover the performers who make the difference when it matters most through Bayesian credibility modeling.
        </p>

        {/* Action Buttons */}
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/dashboard"
            className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-gradient-to-r from-[#FFC928] to-[#E5B422] text-[#1C1D20] text-sm font-bold uppercase tracking-wider shadow-sunshine-md hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center space-x-2 group"
          >
            <span>Explore Clutch IQ</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
          <Link
            to="/archetypes"
            className="w-full sm:w-auto px-8 py-3.5 rounded-2xl glass-panel text-[#F2F4F1] text-sm font-semibold uppercase tracking-wider hover:bg-white/10 hover:border-[#FFC928]/40 transition-all flex items-center justify-center space-x-2"
          >
            <span>Discover Player Archetypes</span>
          </Link>
        </div>

        {/* Hero Macro Stats Grid */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-5 gap-3 max-w-5xl mx-auto">
          {[
            { label: 'Total Matches', val: metadata?.total_matches || '883', sub: 'Across 14 Tournaments' },
            { label: 'Registered Players', val: metadata?.total_registered_players || '1,217', sub: 'In Cleaned Rosters' },
            { label: 'Deliveries Bowled', val: '200,999', sub: 'Regular + Super Overs' },
            { label: 'Pressure Batters', val: metadata?.pressure_batters_count || '775', sub: '249 Primary Cohort' },
            { label: 'Pressure Bowlers', val: metadata?.pressure_bowlers_count || '543', sub: '219 Primary Cohort' },
          ].map((stat, i) => (
            <GlassCard key={i} className="p-4 text-center space-y-1" hover={false}>
              <div className="text-2xl sm:text-3xl font-extrabold text-[#F2F4F1] font-mono">
                {stat.val}
              </div>
              <div className="text-xs font-bold text-[#FFC928] uppercase tracking-wider font-display">
                {stat.label}
              </div>
              <div className="text-[10px] text-[#A6A9A5]">
                {stat.sub}
              </div>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* 2. WHAT IS CLUTCH IQ */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-2">
          <h2 className="text-xs uppercase tracking-widest text-[#FFC928] font-bold font-display">
            Scientific Foundation
          </h2>
          <h3 className="text-3xl sm:text-4xl font-black text-[#F2F4F1] font-display">
            WHAT IS CLUTCH IQ?
          </h3>
          <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
            Raw averages deceive in high-stress match situations. Clutch IQ measures relative performance elevation above a player’s personal baseline, adjusted for sample size using empirical Bayes credibility shrinkage.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <GlassCard className="p-6 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-[#FFC928]/15 border border-[#FFC928]/30 flex items-center justify-center text-[#FFC928]">
              <Target className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-[#F2F4F1] font-display">
              Situational Pressure Isolation
            </h4>
            <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
              Pressure is defined strictly in-match without outcome leakage: Death Overs (16–20), Close Chases (RRR $\ge$ 9 with $\le$ 36 balls), and Knockout matches.
            </p>
          </GlassCard>

          <GlassCard className="p-6 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-[#FFC928]/15 border border-[#FFC928]/30 flex items-center justify-center text-[#FFC928]">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-[#F2F4F1] font-display">
              Bayesian Credibility Shrinkage
            </h4>
            <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
              Small samples pull toward the population mean ($w_i = n / (n + 150)$ for batters, $n / (n + 120)$ for bowlers). Small samples cannot artificially top the leaderboard.
            </p>
          </GlassCard>

          <GlassCard className="p-6 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-[#FFC928]/15 border border-[#FFC928]/30 flex items-center justify-center text-[#FFC928]">
              <Layers className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-[#F2F4F1] font-display">
              Unsupervised Archetyping
            </h4>
            <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
              K-Means clustering discovers natural player personas based on boundary rate, dot-ball percentage, run scoring tempo, and wicket strike rates.
            </p>
          </GlassCard>
        </div>
      </section>

      {/* 3. TOP PERFORMERS PREVIEW */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
          <div>
            <h2 className="text-xs uppercase tracking-widest text-[#FFC928] font-bold font-display">
              Empirical Leaders
            </h2>
            <h3 className="text-2xl sm:text-3xl font-black text-[#F2F4F1] font-display">
              TOP CLUTCH PERFORMERS
            </h3>
          </div>
          <Link
            to="/leaderboards"
            className="inline-flex items-center space-x-1.5 text-xs font-semibold uppercase tracking-wider text-[#FFC928] hover:text-[#FFE27B] transition-colors"
          >
            <span>View Full Leaderboards (Top 10)</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top Batters */}
          <GlassCard className="p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center space-x-2">
                <Trophy className="w-5 h-5 text-[#FFC928]" />
                <h4 className="text-base font-bold text-[#F2F4F1] font-display">Top Pressure Batters</h4>
              </div>
              <span className="text-[10px] uppercase tracking-wider text-[#A6A9A5] font-mono">Primary Cohort (&ge; 50 Balls)</span>
            </div>

            <div className="space-y-3">
              {topBatters.length > 0 ? (
                topBatters.map((player) => (
                  <Link
                    key={player.player_id}
                    to={`/players/${player.player_id}`}
                    className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-[#FFC928]/30 transition-all group"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="w-6 h-6 rounded-md bg-white/10 text-xs font-mono font-bold flex items-center justify-center text-[#F2F4F1]">
                        #{player.rank}
                      </span>
                      <div>
                        <div className="text-sm font-bold text-[#F2F4F1] group-hover:text-[#FFC928] transition-colors">
                          {player.player_name}
                        </div>
                        <div className="text-[11px] text-[#A6A9A5]">
                          SR {player.strike_rate} • {player.balls_faced} balls
                        </div>
                      </div>
                    </div>
                    <ClutchBadge score={player.clutch_iq} size="sm" showLabel={false} />
                  </Link>
                ))
              ) : (
                <div className="py-6 text-center text-xs text-[#A6A9A5]">Loading top batters...</div>
              )}
            </div>
          </GlassCard>

          {/* Top Bowlers */}
          <GlassCard className="p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-[#FFC928]" />
                <h4 className="text-base font-bold text-[#F2F4F1] font-display">Top Pressure Bowlers</h4>
              </div>
              <span className="text-[10px] uppercase tracking-wider text-[#A6A9A5] font-mono">Primary Cohort (&ge; 50 Balls)</span>
            </div>

            <div className="space-y-3">
              {topBowlers.length > 0 ? (
                topBowlers.map((player) => (
                  <Link
                    key={player.player_id}
                    to={`/players/${player.player_id}`}
                    className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-[#FFC928]/30 transition-all group"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="w-6 h-6 rounded-md bg-white/10 text-xs font-mono font-bold flex items-center justify-center text-[#F2F4F1]">
                        #{player.rank}
                      </span>
                      <div>
                        <div className="text-sm font-bold text-[#F2F4F1] group-hover:text-[#FFC928] transition-colors">
                          {player.player_name}
                        </div>
                        <div className="text-[11px] text-[#A6A9A5]">
                          Econ {player.economy_rate} • {player.legal_balls} balls
                        </div>
                      </div>
                    </div>
                    <ClutchBadge score={player.clutch_iq} size="sm" showLabel={false} />
                  </Link>
                ))
              ) : (
                <div className="py-6 text-center text-xs text-[#A6A9A5]">Loading top bowlers...</div>
              )}
            </div>
          </GlassCard>
        </div>
      </section>

      {/* 4. PLAYER ARCHETYPES TEASER */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass-panel-elevated rounded-3xl p-8 sm:p-12 relative overflow-hidden">
          <div className="max-w-2xl space-y-4 relative z-10">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs text-[#FFC928] font-bold">
              <span>Phase 4 Machine Learning Engine</span>
            </div>
            <h3 className="text-3xl sm:text-4xl font-black text-[#F2F4F1] font-display leading-tight">
              UNSUPERVISED PLAYER PROFILING & ARCHETYPES
            </h3>
            <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
              Every player is categorized into empirical performance clusters derived from independent K-Means models ($K=3$ for Batting, $K=3$ for Bowling). Discover high-strike-rate finishers, economical pressure controllers, and anchor accumulators.
            </p>
            <div className="pt-2">
              <Link
                to="/archetypes"
                className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-[#FFC928] text-[#1C1D20] text-xs font-bold uppercase tracking-wider shadow-sunshine-sm hover:scale-[1.02] transition-transform"
              >
                <span>Explore All 6 Archetypes</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 5. CALL TO ACTION SECTION */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
        <h3 className="text-3xl sm:text-5xl font-black text-[#F2F4F1] font-display">
          READY TO ANALYSE PRESSURE?
        </h3>
        <p className="text-sm text-[#A6A9A5] max-w-xl mx-auto leading-relaxed">
          Explore complete leaderboards, compare head-to-head records across 1,217 players, and inspect the empirical cricket models.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <Link
            to="/dashboard"
            className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-[#FFC928] text-[#1C1D20] text-sm font-bold uppercase tracking-wider shadow-sunshine-md hover:scale-[1.02] transition-transform"
          >
            Open Live Dashboard
          </Link>
          <Link
            to="/methodology"
            className="w-full sm:w-auto px-8 py-3.5 rounded-2xl glass-panel text-[#F2F4F1] text-sm font-semibold uppercase tracking-wider hover:bg-white/10 transition-all"
          >
            View Research Methodology
          </Link>
        </div>
      </section>
    </div>
  );
}

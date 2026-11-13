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
  ChevronRight,
  ShieldAlert,
  Compass
} from 'lucide-react';
import api from '../services/api';
import ClutchBadge from '../components/ClutchBadge';
import GlassCard from '../components/GlassCard';

function formatNum(val, decimals = 1) {
  if (val === null || val === undefined) return '—';
  const num = typeof val === 'number' ? val : parseFloat(val);
  return isNaN(num) ? '—' : num.toFixed(decimals);
}

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
          api.getBattersLeaderboard({ page: 1, page_size: 4, cohort: 'primary' }).catch(() => ({ items: [] })),
          api.getBowlersLeaderboard({ page: 1, page_size: 4, cohort: 'primary' }).catch(() => ({ items: [] })),
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
    <div className="relative overflow-hidden space-y-20 sm:space-y-28">
      {/* Dynamic Golden Sunshine Atmospheric Highlights */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[700px] bg-gradient-to-b from-[#FFC928]/15 via-[#FFC928]/5 to-transparent blur-[120px] pointer-events-none -z-10" />
      <div className="absolute top-96 right-10 w-[500px] h-[500px] bg-[#FFC928]/10 rounded-full blur-[140px] pointer-events-none -z-10" />

      {/* 1. CINEMATIC HERO SECTION WITH 3D STADIUM & ACTION SHOWCASE */}
      <section className="relative rounded-3xl overflow-hidden border border-white/10 bg-gradient-to-b from-[#1C1D20]/90 via-[#25262A]/80 to-[#1C1D20]">
        {/* Background 3D Stadium Render with Golden-Yellow Floodlight Reflection */}
        <div className="absolute inset-0 z-0">
          <img 
            src="/images/stadium_hero.png" 
            alt="3D Cricket Stadium at Night with Golden Sunshine Reflections" 
            className="w-full h-full object-cover object-center opacity-35 mix-blend-screen scale-105 transition-transform duration-1000 ease-out hover:scale-100"
          />
          {/* Vignette Gradients for Text Legibility & Contrast */}
          <div className="absolute inset-0 bg-gradient-to-r from-[#1C1D20] via-[#1C1D20]/80 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#1C1D20] via-transparent to-[#1C1D20]/60" />
          <div className="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-[#1C1D20] to-transparent" />
        </div>

        {/* Hero Content Container */}
        <div className="relative z-10 px-6 sm:px-10 lg:px-14 py-16 sm:py-24 max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Column: Editorial Headline & Punchy Intro */}
            <div className="lg:col-span-7 space-y-6 text-left">
              {/* Event & Category Pill */}
              <div className="inline-flex items-center space-x-2.5 px-4 py-1.5 rounded-full bg-[#1C1D20]/80 border border-[#FFC928]/30 backdrop-blur-md shadow-sunshine-sm">
                <Sparkles className="w-4 h-4 text-[#FFC928] animate-pulse" />
                <span className="text-xs uppercase tracking-widest text-[#FFC928] font-bold font-sans">
                  Rajasthan Royals Hackathon
                </span>
                <span className="text-xs text-[#A6A9A5] font-sans">• Empirical Pressure Engine</span>
              </div>

              {/* Bold Archivo Headline */}
              <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black font-sans tracking-tight text-[#F2F4F1] uppercase leading-[0.95]">
                BEYOND <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FFC928] via-[#FFE27B] to-[#FFC928] sunshine-text-glow">
                  STATISTICS.
                </span>
              </h1>

              {/* Secondary Subtitle */}
              <p className="text-lg sm:text-2xl font-bold text-[#F2F4F1] font-sans tracking-tight">
                Discovering Players Who Perform Under Pressure.
              </p>

              {/* Concise Pitch */}
              <p className="text-sm sm:text-base text-[#A6A9A5] font-sans max-w-xl leading-relaxed">
                When the required rate climbs and championship moments arrive, aggregate stats tell half the story. 
                <span className="text-[#F2F4F1] font-semibold"> Clutch IQ</span> isolates high-pressure match scenarios using Bayesian empirical credibility shrinkage and machine learning archetypes.
              </p>

              {/* Action Buttons */}
              <div className="pt-2 flex flex-wrap items-center gap-4">
                <Link
                  to="/dashboard"
                  className="px-8 py-3.5 rounded-2xl bg-gradient-to-r from-[#FFC928] to-[#E5B422] text-[#1C1D20] text-sm font-black uppercase tracking-wider shadow-sunshine-md hover:scale-[1.03] active:scale-[0.98] transition-all flex items-center space-x-2.5 group"
                >
                  <Flame className="w-4 h-4 text-[#1C1D20]" />
                  <span>Launch Dashboard</span>
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </Link>

                <Link
                  to="/leaderboards"
                  className="px-7 py-3.5 rounded-2xl glass-panel text-[#F2F4F1] text-sm font-bold uppercase tracking-wider hover:bg-white/10 hover:border-[#FFC928]/40 transition-all flex items-center space-x-2"
                >
                  <Trophy className="w-4 h-4 text-[#FFC928]" />
                  <span>Top 10 Rankings</span>
                </Link>
              </div>

              {/* Micro Metric Ticker */}
              <div className="pt-6 border-t border-white/10 grid grid-cols-3 gap-4 max-w-lg">
                <div>
                  <div className="text-2xl sm:text-3xl font-black text-[#F2F4F1] font-sans">
                    {metadata?.total_matches || '883'}
                  </div>
                  <div className="text-[11px] text-[#FFC928] uppercase font-bold tracking-wider">
                    Matches Tracked
                  </div>
                </div>
                <div>
                  <div className="text-2xl sm:text-3xl font-black text-[#F2F4F1] font-sans">
                    {metadata?.total_registered_players || '1,217'}
                  </div>
                  <div className="text-[11px] text-[#FFC928] uppercase font-bold tracking-wider">
                    Players Indexed
                  </div>
                </div>
                <div>
                  <div className="text-2xl sm:text-3xl font-black text-[#F2F4F1] font-sans">
                    26.6%
                  </div>
                  <div className="text-[11px] text-[#FFC928] uppercase font-bold tracking-wider">
                    Pressure Volume
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: 3D Holographic Card Preview with Batsman in Action */}
            <div className="lg:col-span-5 relative">
              {/* Radial Glow Halo Behind Card */}
              <div className="absolute -inset-2 bg-gradient-to-tr from-[#FFC928]/30 via-transparent to-[#FFC928]/10 rounded-3xl blur-2xl -z-10" />

              <div className="glass-panel-elevated rounded-3xl p-4 sm:p-5 border border-white/15 relative overflow-hidden group">
                {/* 3D Action Image Container */}
                <div className="relative rounded-2xl overflow-hidden aspect-[4/3] bg-[#1C1D20] border border-white/10">
                  <img 
                    src="/images/player_clutch_action.png" 
                    alt="3D Cricket Batsman Delivering in Clutch Moment" 
                    className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700 ease-out"
                  />
                  {/* Subtle Golden Sheen Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-[#1C1D20] via-transparent to-transparent opacity-80" />
                  
                  {/* Top Live Match Situation Tag */}
                  <div className="absolute top-3 left-3 flex items-center space-x-1.5 px-3 py-1 rounded-full bg-[#1C1D20]/85 border border-[#FFC928]/40 backdrop-blur-md">
                    <span className="w-2 h-2 rounded-full bg-[#FFC928] animate-ping" />
                    <span className="text-[11px] font-bold text-[#FFC928] uppercase tracking-wider font-sans">
                      Match Defining Moment
                    </span>
                  </div>

                  {/* Bottom Stats Overlay inside image */}
                  <div className="absolute bottom-3 inset-x-3 flex items-end justify-between">
                    <div>
                      <div className="text-xs uppercase font-bold text-[#A6A9A5] tracking-widest">
                        Pressure Impact
                      </div>
                      <div className="text-xl font-black text-[#F2F4F1] font-sans">
                        Death Overs (16–20)
                      </div>
                    </div>
                    <div className="px-3 py-1.5 rounded-xl bg-[#FFC928] text-[#1C1D20] font-black text-sm tracking-tight shadow-sunshine-sm font-sans">
                      RRR &gt; 9.5
                    </div>
                  </div>
                </div>

                {/* Card Bottom Meta Bar */}
                <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-[#FFC928]/20 border border-[#FFC928]/40 flex items-center justify-center text-[#FFC928]">
                      <Zap className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-bold text-[#F2F4F1]">Bayesian Prior Normalization</div>
                      <div className="text-[10px] text-[#A6A9A5]">Sample-size regularized deltas</div>
                    </div>
                  </div>
                  <Link 
                    to="/methodology" 
                    className="text-[#FFC928] hover:text-[#FFE27B] font-bold uppercase text-[11px] flex items-center space-x-1"
                  >
                    <span>Formula</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 2. THREE-PILLAR 3D VISUAL SHOWCASE (IMAGE-FORWARD CARDS) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
        <div className="text-center max-w-3xl mx-auto space-y-2">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-[#FFC928]/10 border border-[#FFC928]/20 text-[#FFC928] text-xs font-bold uppercase tracking-widest font-sans">
            <Compass className="w-3.5 h-3.5" />
            <span>The Three Analytical Pillars</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-black text-[#F2F4F1] font-sans tracking-tight">
            CRICKET INTELLIGENCE RE-ENGINEERED
          </h2>
          <p className="text-sm text-[#A6A9A5] font-sans">
            A comprehensive, multi-dimensional framework addressing situational context, empirical credibility, and tactical player personas.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
          
          {/* Card 1: 3D Cricket Pitch Image (Situational Pressure Isolation) */}
          <div className="glass-panel-elevated rounded-3xl overflow-hidden border border-white/10 hover:border-[#FFC928]/40 transition-all group flex flex-col">
            <div className="relative h-48 overflow-hidden bg-[#1C1D20]">
              <img 
                src="/images/cricket_pitch_3d.png" 
                alt="3D Cricket Pitch and Wickets under Golden Sunshine" 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#25262A] via-transparent to-transparent" />
              <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-[#1C1D20]/80 border border-white/15 text-[11px] font-bold text-[#FFC928] backdrop-blur-md">
                53,453 Pressure Deliveries
              </div>
            </div>
            <div className="p-6 flex-1 flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-[#FFC928]">
                  <Target className="w-5 h-5" />
                  <span className="text-xs uppercase font-bold tracking-wider">In-Match Context</span>
                </div>
                <h3 className="text-xl font-black text-[#F2F4F1] font-sans">
                  Situational Pressure Isolation
                </h3>
                <p className="text-xs sm:text-sm text-[#A6A9A5] font-sans leading-relaxed">
                  Deliveries are isolated across 8 high-stress match states: Death Overs (16–20), Close Chases ($RRR &gt; 9.0$), Top-Order Collapses ($\le 30/3$), and Playoff Knockouts.
                </p>
              </div>
              <Link 
                to="/analytics" 
                className="pt-2 inline-flex items-center space-x-1.5 text-xs font-bold text-[#FFC928] group-hover:text-[#FFE27B] uppercase tracking-wider"
              >
                <span>Explore 8 Situations</span>
                <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>

          {/* Card 2: 3D Batsman Image (Empirical Bayes Shrinkage) */}
          <div className="glass-panel-elevated rounded-3xl overflow-hidden border border-white/10 hover:border-[#FFC928]/40 transition-all group flex flex-col">
            <div className="relative h-48 overflow-hidden bg-[#1C1D20]">
              <img 
                src="/images/player_clutch_action.png" 
                alt="3D Cricket Player Striking Under Pressure" 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#25262A] via-transparent to-transparent" />
              <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-[#1C1D20]/80 border border-white/15 text-[11px] font-bold text-[#FFC928] backdrop-blur-md">
                Empirical Credibility
              </div>
            </div>
            <div className="p-6 flex-1 flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-[#FFC928]">
                  <TrendingUp className="w-5 h-5" />
                  <span className="text-xs uppercase font-bold tracking-wider">Mathematical Rigor</span>
                </div>
                <h3 className="text-xl font-black text-[#F2F4F1] font-sans">
                  Bayesian Shrinkage Normalization
                </h3>
                <p className="text-xs sm:text-sm text-[#A6A9A5] font-sans leading-relaxed">
                  Small-sample noise is penalized through credibility weight w_i = N_i / (N_i + M) with M=120 (batting) and M=90 (bowling). Only sustained pressure performers reach the elite rankings.
                </p>
              </div>
              <Link 
                to="/methodology" 
                className="pt-2 inline-flex items-center space-x-1.5 text-xs font-bold text-[#FFC928] group-hover:text-[#FFE27B] uppercase tracking-wider"
              >
                <span>Inspect Mathematical Proofs</span>
                <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>

          {/* Card 3: 3D Stadium Image (Unsupervised ML Archetypes) */}
          <div className="glass-panel-elevated rounded-3xl overflow-hidden border border-white/10 hover:border-[#FFC928]/40 transition-all group flex flex-col">
            <div className="relative h-48 overflow-hidden bg-[#1C1D20]">
              <img 
                src="/images/stadium_hero.png" 
                alt="3D Stadium Arena with Volumetric Sunshine Rays" 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#25262A] via-transparent to-transparent" />
              <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-[#1C1D20]/80 border border-white/15 text-[11px] font-bold text-[#FFC928] backdrop-blur-md">
                K-Means (K=3) Models
              </div>
            </div>
            <div className="p-6 flex-1 flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-[#FFC928]">
                  <Layers className="w-5 h-5" />
                  <span className="text-xs uppercase font-bold tracking-wider">Scouting & Profiling</span>
                </div>
                <h3 className="text-xl font-black text-[#F2F4F1] font-sans">
                  6 Machine Learning Archetypes
                </h3>
                <p className="text-xs sm:text-sm text-[#A6A9A5] font-sans leading-relaxed">
                  Players are grouped into data-driven tactical clusters: Volatile Finishers, Anchor Stabilizers, Death Specialists, and Defensive Controllers for auction decisions.
                </p>
              </div>
              <Link 
                to="/archetypes" 
                className="pt-2 inline-flex items-center space-x-1.5 text-xs font-bold text-[#FFC928] group-hover:text-[#FFE27B] uppercase tracking-wider"
              >
                <span>Scout Player Archetypes</span>
                <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>

        </div>
      </section>

      {/* 3. TOP PERFORMERS PODIUM PREVIEW */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 text-xs font-bold text-[#FFC928] uppercase tracking-widest font-sans">
              <Trophy className="w-4 h-4" />
              <span>Validated Leaders</span>
            </div>
            <h2 className="text-2xl sm:text-4xl font-black text-[#F2F4F1] font-sans tracking-tight">
              PROVEN PRESSURE PERFORMERS
            </h2>
          </div>
          <Link
            to="/leaderboards"
            className="inline-flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-[#FFC928] hover:text-[#FFE27B] transition-colors"
          >
            <span>View Full Leaderboards (Top 10)</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top Batters Showcase */}
          <div className="glass-panel-elevated rounded-3xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-xl bg-[#FFC928]/20 flex items-center justify-center text-[#FFC928]">
                  <Flame className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-black text-[#F2F4F1] font-sans">Top Batting Performers</h3>
                  <p className="text-[10px] text-[#A6A9A5]">Primary Cohort (Min 120 Pressure Balls)</p>
                </div>
              </div>
              <span className="text-[10px] uppercase font-bold text-[#FFC928] bg-[#FFC928]/10 px-2.5 py-1 rounded-full border border-[#FFC928]/20">
                Clutch IQ
              </span>
            </div>

            <div className="space-y-2.5">
              {topBatters.length > 0 ? (
                topBatters.map((player) => (
                  <Link
                    key={player.player_id}
                    to={`/players/${player.player_id}`}
                    className="flex items-center justify-between p-3 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-[#FFC928]/40 transition-all group"
                  >
                    <div className="flex items-center space-x-3.5">
                      <span className={`w-7 h-7 rounded-lg text-xs font-bold font-sans flex items-center justify-center ${
                        player.rank === 1 
                          ? 'bg-[#FFC928] text-[#1C1D20] shadow-sunshine-sm' 
                          : 'bg-white/10 text-[#F2F4F1]'
                      }`}>
                        #{player.rank}
                      </span>
                      <div>
                        <div className="text-sm font-bold text-[#F2F4F1] group-hover:text-[#FFC928] transition-colors font-sans">
                          {player.player_name}
                        </div>
                        <div className="text-[11px] text-[#A6A9A5] font-sans">
                          Avg {formatNum(player.batting_average, 1)} • SR {formatNum(player.strike_rate, 1)} • {player.balls_faced || '—'} balls
                        </div>
                      </div>
                    </div>
                    <ClutchBadge score={player.clutch_iq} size="sm" showLabel={false} />
                  </Link>
                ))
              ) : (
                <div className="py-8 text-center text-xs text-[#A6A9A5]">Loading top batters...</div>
              )}
            </div>
          </div>

          {/* Top Bowlers Showcase */}
          <div className="glass-panel-elevated rounded-3xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-xl bg-[#FFC928]/20 flex items-center justify-center text-[#FFC928]">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-black text-[#F2F4F1] font-sans">Top Bowling Performers</h3>
                  <p className="text-[10px] text-[#A6A9A5]">Primary Cohort (Min 90 Pressure Balls)</p>
                </div>
              </div>
              <span className="text-[10px] uppercase font-bold text-[#FFC928] bg-[#FFC928]/10 px-2.5 py-1 rounded-full border border-[#FFC928]/20">
                Clutch IQ
              </span>
            </div>

            <div className="space-y-2.5">
              {topBowlers.length > 0 ? (
                topBowlers.map((player) => (
                  <Link
                    key={player.player_id}
                    to={`/players/${player.player_id}`}
                    className="flex items-center justify-between p-3 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-[#FFC928]/40 transition-all group"
                  >
                    <div className="flex items-center space-x-3.5">
                      <span className={`w-7 h-7 rounded-lg text-xs font-bold font-sans flex items-center justify-center ${
                        player.rank === 1 
                          ? 'bg-[#FFC928] text-[#1C1D20] shadow-sunshine-sm' 
                          : 'bg-white/10 text-[#F2F4F1]'
                      }`}>
                        #{player.rank}
                      </span>
                      <div>
                        <div className="text-sm font-bold text-[#F2F4F1] group-hover:text-[#FFC928] transition-colors font-sans">
                          {player.player_name}
                        </div>
                        <div className="text-[11px] text-[#A6A9A5] font-sans">
                          Econ {formatNum(player.economy_rate, 2)} • SR {formatNum(player.bowling_strike_rate, 1)} • {player.legal_balls || '—'} balls
                        </div>
                      </div>
                    </div>
                    <ClutchBadge score={player.clutch_iq} size="sm" showLabel={false} />
                  </Link>
                ))
              ) : (
                <div className="py-8 text-center text-xs text-[#A6A9A5]">Loading top bowlers...</div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* 4. IMMERSIVE ARCHETYPE STUDIO BANNER WITH STADIUM VISUAL */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative rounded-3xl overflow-hidden border border-white/15 bg-gradient-to-r from-[#1C1D20] via-[#25262A] to-[#1C1D20] p-8 sm:p-14">
          {/* Background 3D Stadium Glow Layer */}
          <div className="absolute inset-0 z-0">
            <img 
              src="/images/stadium_hero.png" 
              alt="Stadium Night Lights" 
              className="w-full h-full object-cover object-right opacity-20 mix-blend-screen scale-110"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-[#1C1D20] via-[#1C1D20]/90 to-transparent" />
          </div>

          <div className="relative z-10 max-w-2xl space-y-5">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs text-[#FFC928] font-bold font-sans">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Machine Learning Scouting Dossier</span>
            </div>

            <h3 className="text-3xl sm:text-5xl font-black text-[#F2F4F1] font-sans tracking-tight leading-tight">
              UNSUPERVISED PLAYER ARCHETYPING
            </h3>

            <p className="text-sm text-[#A6A9A5] font-sans leading-relaxed">
              IPL teams cannot rely on generic role classifications. Our K-Means clustering algorithm maps all 1,217 players into 6 actionable strategic archetypes based on boundary frequency, dot-ball containment, and pressure acceleration.
            </p>

            {/* Quick Archetype Pills */}
            <div className="flex flex-wrap gap-2 pt-2">
              {[
                'Volatile Finishers',
                'Anchor Stabilizers',
                'Balanced Accumulators',
                'Death Specialists',
                'Defensive Controllers',
                'Volume Strike Bowlers'
              ].map((name, idx) => (
                <span 
                  key={idx}
                  className="px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-xs font-semibold text-[#F2F4F1] font-sans"
                >
                  {name}
                </span>
              ))}
            </div>

            <div className="pt-4">
              <Link
                to="/archetypes"
                className="inline-flex items-center space-x-2 px-8 py-3.5 rounded-2xl bg-[#FFC928] text-[#1C1D20] text-xs font-black uppercase tracking-wider shadow-sunshine-md hover:scale-[1.02] active:scale-[0.98] transition-all font-sans"
              >
                <span>Scout All 6 Archetypes</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 5. CALL TO ACTION SECTION */}
      <section className="relative rounded-3xl overflow-hidden border border-white/10 max-w-5xl mx-auto px-6 py-14 sm:py-20 text-center space-y-6 bg-gradient-to-b from-[#25262A]/60 via-[#1C1D20] to-[#1C1D20]">
        <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-transparent via-[#FFC928] to-transparent" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-96 h-32 bg-[#FFC928]/10 blur-3xl pointer-events-none -z-10" />

        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-[#FFC928] font-bold font-sans">
          <span>Ready For In-Depth Analysis?</span>
        </div>

        <h3 className="text-3xl sm:text-5xl font-black text-[#F2F4F1] font-sans tracking-tight">
          TEST YOUR PLAYERS UNDER PRESSURE
        </h3>

        <p className="text-sm sm:text-base text-[#A6A9A5] font-sans max-w-xl mx-auto leading-relaxed">
          Search, filter, and compare head-to-head records across 1,217 players with full mathematical transparency.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            to="/players"
            className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-[#FFC928] text-[#1C1D20] text-sm font-black uppercase tracking-wider shadow-sunshine-md hover:scale-[1.02] transition-transform font-sans flex items-center justify-center space-x-2"
          >
            <Search className="w-4 h-4" />
            <span>Search Player Directory</span>
          </Link>
          <Link
            to="/compare"
            className="w-full sm:w-auto px-8 py-4 rounded-2xl glass-panel text-[#F2F4F1] text-sm font-bold uppercase tracking-wider hover:bg-white/10 border border-white/10 hover:border-[#FFC928]/40 transition-all font-sans flex items-center justify-center space-x-2"
          >
            <Layers className="w-4 h-4 text-[#FFC928]" />
            <span>Compare Head-to-Head</span>
          </Link>
        </div>
      </section>
    </div>
  );
}

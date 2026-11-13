import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Trophy, 
  ShieldCheck, 
  Flame, 
  Sparkles, 
  Scale, 
  ArrowLeft, 
  TrendingUp, 
  BarChart2, 
  Calendar, 
  CheckCircle2,
  Info
} from 'lucide-react';
import api from '../services/api';
import GlassCard from '../components/GlassCard';
import ClutchBadge from '../components/ClutchBadge';
import { CardSkeleton } from '../components/LoadingSkeleton';
import ErrorMessage from '../components/ErrorMessage';

export default function PlayerDetailPage() {
  const { id } = useParams();
  const playerId = parseInt(id, 10);

  const [summary, setSummary] = useState(null);
  const [batting, setBatting] = useState(null);
  const [bowling, setBowling] = useState(null);
  const [activeTab, setActiveTab] = useState('batting'); // 'batting' or 'bowling'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadPlayer() {
      setLoading(true);
      setError(null);
      try {
        const sumRes = await api.getPlayerSummary(playerId);
        setSummary(sumRes);

        // Fetch batting and bowling conditionally
        const promises = [];
        if (sumRes.has_batting_profile) {
          promises.push(api.getPlayerBattingProfile(playerId).then(setBatting).catch(() => null));
        }
        if (sumRes.has_bowling_profile) {
          promises.push(api.getPlayerBowlingProfile(playerId).then(setBowling).catch(() => null));
        }

        await Promise.all(promises);

        // Set default active tab based on what's available
        if (sumRes.has_batting_profile) {
          setActiveTab('batting');
        } else if (sumRes.has_bowling_profile) {
          setActiveTab('bowling');
        }
      } catch (err) {
        console.error('Failed to load player details:', err);
        setError(err.message || 'Player not found');
      } finally {
        setLoading(false);
      }
    }
    loadPlayer();
  }, [playerId]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
        <div className="h-6 bg-white/10 rounded w-24 animate-pulse"></div>
        <CardSkeleton rows={8} />
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <ErrorMessage title="Player Profile Unavailable" message={error || 'Player record not found.'} />
        <div className="text-center mt-4">
          <Link to="/players" className="text-xs uppercase tracking-wider font-semibold text-[#FFC928] hover:underline">
            &larr; Back to Player Explorer
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* 1. Breadcrumb & Back Link */}
      <div className="flex items-center justify-between">
        <Link
          to="/players"
          className="inline-flex items-center space-x-1.5 text-xs font-semibold uppercase tracking-wider text-[#A6A9A5] hover:text-[#F2F4F1] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Player Explorer</span>
        </Link>

        <Link
          to={`/compare?player_ids=${playerId}`}
          className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-[#F2F4F1] transition-all"
        >
          <Scale className="w-3.5 h-3.5 text-[#FFC928]" />
          <span>Compare this Player</span>
        </Link>
      </div>

      {/* 2. Hero Profile Card */}
      <GlassCard className="p-6 sm:p-8 space-y-6" hover={false}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-white/10">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-md bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs font-mono font-bold text-[#FFC928]">
                ID: {summary.player_id}
              </span>
              {summary.has_batting_profile && summary.has_bowling_profile && (
                <span className="px-2.5 py-0.5 rounded-md bg-emerald-500/15 border border-emerald-500/30 text-xs font-semibold text-emerald-400">
                  All-Rounder
                </span>
              )}
            </div>

            <h1 className="text-3xl sm:text-5xl font-black font-display text-[#F2F4F1] tracking-tight">
              {summary.player_name}
            </h1>

            {/* Teams & Competitions */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-[#A6A9A5]">
              {summary.teams && summary.teams.length > 0 && (
                <div className="flex items-center space-x-1">
                  <span className="text-[#F2F4F1] font-semibold">{summary.teams.join(', ')}</span>
                </div>
              )}
              {summary.competitions && summary.competitions.length > 0 && (
                <>
                  <span>•</span>
                  <span>{summary.competitions.slice(0, 3).join(', ')}{summary.competitions.length > 3 ? ` +${summary.competitions.length - 3} more` : ''}</span>
                </>
              )}
            </div>
          </div>

          {/* Clutch IQ Badges Group */}
          <div className="flex flex-row md:flex-col items-center md:items-end gap-3">
            {summary.has_batting_profile && (
              <div className="text-right">
                <span className="text-[10px] uppercase tracking-wider text-[#A6A9A5] block font-mono">Batting Clutch IQ</span>
                <ClutchBadge
                  score={summary.batting_clutch_iq}
                  rank={summary.batting_rank}
                  cohort={summary.batting_cohort}
                  size="lg"
                />
              </div>
            )}
            {summary.has_bowling_profile && (
              <div className="text-right">
                <span className="text-[10px] uppercase tracking-wider text-[#A6A9A5] block font-mono">Bowling Clutch IQ</span>
                <ClutchBadge
                  score={summary.bowling_clutch_iq}
                  rank={summary.bowling_rank}
                  cohort={summary.bowling_cohort}
                  size="lg"
                />
              </div>
            )}
          </div>
        </div>

        {/* Role Tabs */}
        <div className="flex items-center space-x-3">
          {summary.has_batting_profile && (
            <button
              onClick={() => setActiveTab('batting')}
              className={`px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold uppercase tracking-wider transition-all flex items-center space-x-2 ${
                activeTab === 'batting'
                  ? 'bg-[#FFC928] text-[#1C1D20] shadow-sunshine-sm'
                  : 'bg-white/5 text-[#A6A9A5] hover:text-[#F2F4F1] hover:bg-white/10'
              }`}
            >
              <Trophy className="w-4 h-4" />
              <span>Pressure Batting Profile</span>
            </button>
          )}

          {summary.has_bowling_profile && (
            <button
              onClick={() => setActiveTab('bowling')}
              className={`px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold uppercase tracking-wider transition-all flex items-center space-x-2 ${
                activeTab === 'bowling'
                  ? 'bg-[#FFC928] text-[#1C1D20] shadow-sunshine-sm'
                  : 'bg-white/5 text-[#A6A9A5] hover:text-[#F2F4F1] hover:bg-white/10'
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Pressure Bowling Profile</span>
            </button>
          )}
        </div>
      </GlassCard>

      {/* 3. Deep Role Analytics */}
      {activeTab === 'batting' && batting && (
        <div className="space-y-8">
          {/* Archetype Narrative Card */}
          <GlassCard className="p-6 border-[#FFC928]/30 space-y-2" hover={false}>
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-widest text-[#FFC928] font-bold font-display">
                Phase 4 Batting Archetype
              </span>
              <span className="text-xs font-mono font-semibold text-[#A6A9A5]">
                Status: <span className="text-[#F2F4F1] uppercase">{batting.assignment_status}</span>
              </span>
            </div>
            <h3 className="text-xl font-extrabold text-[#F2F4F1] font-display">
              {batting.archetype_name}
            </h3>
            <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
              {batting.player_archetype_explanation}
            </p>
          </GlassCard>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <GlassCard className="p-5 space-y-1">
              <span className="text-xs text-[#A6A9A5] uppercase tracking-wider font-semibold font-display">Pressure Strike Rate</span>
              <div className="text-3xl font-black text-[#FFC928] font-mono">{batting.strike_rate}</div>
              <div className="text-[11px] text-[#A6A9A5]">
                Baseline: <span className="text-[#F2F4F1] font-mono">{batting.sr_baseline ?? '—'}</span> (Reg: {batting.reg_sr_base})
              </div>
            </GlassCard>

            <GlassCard className="p-5 space-y-1">
              <span className="text-xs text-[#A6A9A5] uppercase tracking-wider font-semibold font-display">Raw Delta SR</span>
              <div className={`text-3xl font-black font-mono ${batting.raw_delta_strike_rate >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {batting.raw_delta_strike_rate > 0 ? `+${batting.raw_delta_strike_rate}` : batting.raw_delta_strike_rate}
              </div>
              <div className="text-[11px] text-[#A6A9A5]">
                Shrunk Delta: <span className="font-mono text-[#F2F4F1]">{batting.shrunk_delta_strike_rate > 0 ? `+${batting.shrunk_delta_strike_rate}` : batting.shrunk_delta_strike_rate}</span>
              </div>
            </GlassCard>

            <GlassCard className="p-5 space-y-1">
              <span className="text-xs text-[#A6A9A5] uppercase tracking-wider font-semibold font-display">Dot Ball %</span>
              <div className="text-3xl font-black text-[#F2F4F1] font-mono">{batting.dot_ball_pct}%</div>
              <div className="text-[11px] text-[#A6A9A5]">
                Baseline Dot: <span className="text-[#F2F4F1] font-mono">{batting.dot_pct_baseline ?? '—'}%</span>
              </div>
            </GlassCard>

            <GlassCard className="p-5 space-y-1">
              <span className="text-xs text-[#A6A9A5] uppercase tracking-wider font-semibold font-display">Boundary %</span>
              <div className="text-3xl font-black text-[#F2F4F1] font-mono">{batting.boundary_ball_pct}%</div>
              <div className="text-[11px] text-[#A6A9A5]">
                {batting.fours} Fours • {batting.sixes} Sixes
              </div>
            </GlassCard>
          </div>

          {/* Sample Size & Reliability Details */}
          <GlassCard className="p-6 space-y-4" hover={false}>
            <h4 className="text-sm uppercase tracking-wider font-bold text-[#F2F4F1] font-display">
              Sample Size & Empirical Bayes Weighting
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs text-[#A6A9A5]">
              <div>
                <span className="block text-[#A6A9A5] mb-1">Pressure Sample</span>
                <span className="text-base font-bold text-[#F2F4F1] font-mono">{batting.balls_faced} balls faced</span>
                <span className="block text-[11px] mt-0.5">Across {batting.match_count} distinct pressure matches ({batting.innings_count} innings)</span>
              </div>

              <div>
                <span className="block text-[#A6A9A5] mb-1">Bayesian Shrinkage Weight (w_i)</span>
                <span className="text-base font-bold text-[#FFC928] font-mono">{batting.reliability_weight}</span>
                <span className="block text-[11px] mt-0.5">Formula: n / (n + 150), scaling confidence</span>
              </div>

              <div>
                <span className="block text-[#A6A9A5] mb-1">Batting Average</span>
                <span className="text-base font-bold text-[#F2F4F1] font-mono">{batting.batting_average ?? 'Undefeated'}</span>
                <span className="block text-[11px] mt-0.5">{batting.total_runs} runs with {batting.dismissals} dismissals</span>
              </div>
            </div>
          </GlassCard>
        </div>
      )}

      {activeTab === 'bowling' && bowling && (
        <div className="space-y-8">
          {/* Archetype Narrative Card */}
          <GlassCard className="p-6 border-[#FFC928]/30 space-y-2" hover={false}>
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-widest text-[#FFC928] font-bold font-display">
                Phase 4 Bowling Archetype
              </span>
              <span className="text-xs font-mono font-semibold text-[#A6A9A5]">
                Status: <span className="text-[#F2F4F1] uppercase">{bowling.assignment_status}</span>
              </span>
            </div>
            <h3 className="text-xl font-extrabold text-[#F2F4F1] font-display">
              {bowling.archetype_name}
            </h3>
            <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
              {bowling.player_archetype_explanation}
            </p>
          </GlassCard>

          {/* Key Bowling Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <GlassCard className="p-5 space-y-1">
              <span className="text-xs text-[#A6A9A5] uppercase tracking-wider font-semibold font-display">Pressure Economy</span>
              <div className="text-3xl font-black text-[#FFC928] font-mono">{bowling.economy_rate}</div>
              <div className="text-[11px] text-[#A6A9A5]">
                Baseline: <span className="text-[#F2F4F1] font-mono">{bowling.econ_baseline ?? '—'}</span> (Reg: {bowling.reg_econ_base})
              </div>
            </GlassCard>

            <GlassCard className="p-5 space-y-1">
              <span className="text-xs text-[#A6A9A5] uppercase tracking-wider font-semibold font-display">Raw Delta Economy</span>
              <div className={`text-3xl font-black font-mono ${bowling.raw_delta_economy >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {bowling.raw_delta_economy > 0 ? `+${bowling.raw_delta_economy}` : bowling.raw_delta_economy}
              </div>
              <div className="text-[11px] text-[#A6A9A5]">
                Shrunk Delta: <span className="font-mono text-[#F2F4F1]">{bowling.shrunk_delta_economy > 0 ? `+${bowling.shrunk_delta_economy}` : bowling.shrunk_delta_economy}</span>
              </div>
            </GlassCard>

            <GlassCard className="p-5 space-y-1">
              <span className="text-xs text-[#A6A9A5] uppercase tracking-wider font-semibold font-display">Wicket Potency</span>
              <div className="text-3xl font-black text-[#F2F4F1] font-mono">{bowling.bowler_wickets} <span className="text-xs font-sans text-[#A6A9A5]">wkts</span></div>
              <div className="text-[11px] text-[#A6A9A5]">
                Strike Rate: <span className="text-[#F2F4F1] font-mono">{bowling.bowling_strike_rate ?? '—'}</span> balls/wkt
              </div>
            </GlassCard>

            <GlassCard className="p-5 space-y-1">
              <span className="text-xs text-[#A6A9A5] uppercase tracking-wider font-semibold font-display">Dot Ball %</span>
              <div className="text-3xl font-black text-[#F2F4F1] font-mono">{bowling.dot_ball_pct}%</div>
              <div className="text-[11px] text-[#A6A9A5]">
                Boundaries conceded: {bowling.boundary_balls_conceded_per_100_legal_balls}/100 balls
              </div>
            </GlassCard>
          </div>

          {/* Sample Size & Reliability Details */}
          <GlassCard className="p-6 space-y-4" hover={false}>
            <h4 className="text-sm uppercase tracking-wider font-bold text-[#F2F4F1] font-display">
              Sample Size & Empirical Bayes Weighting
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs text-[#A6A9A5]">
              <div>
                <span className="block text-[#A6A9A5] mb-1">Pressure Sample</span>
                <span className="text-base font-bold text-[#F2F4F1] font-mono">{bowling.legal_balls} legal balls</span>
                <span className="block text-[11px] mt-0.5">Conceded {bowling.runs_conceded} runs in {bowling.match_count} matches</span>
              </div>

              <div>
                <span className="block text-[#A6A9A5] mb-1">Bayesian Shrinkage Weight (w_i)</span>
                <span className="text-base font-bold text-[#FFC928] font-mono">{bowling.reliability_weight}</span>
                <span className="block text-[11px] mt-0.5">Formula: n / (n + 120), scaling confidence</span>
              </div>

              <div>
                <span className="block text-[#A6A9A5] mb-1">Bowling Average</span>
                <span className="text-base font-bold text-[#F2F4F1] font-mono">{bowling.bowling_average ?? '—'}</span>
                <span className="block text-[11px] mt-0.5">{bowling.wickets_per_legal_ball} wickets per legal ball</span>
              </div>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}

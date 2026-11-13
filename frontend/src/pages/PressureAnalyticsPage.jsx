import React, { useState, useEffect } from 'react';
import { 
  Flame, 
  Layers, 
  BarChart3, 
  TrendingUp, 
  CheckCircle2, 
  AlertCircle,
  Activity,
  Zap,
  Info
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell
} from 'recharts';
import api from '../services/api';
import GlassCard from '../components/GlassCard';
import { CardSkeleton } from '../components/LoadingSkeleton';
import ErrorMessage from '../components/ErrorMessage';

export default function PressureAnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadPressureData() {
      setLoading(true);
      setError(null);
      try {
        const res = await api.getPressureAnalytics();
        setData(res);
      } catch (err) {
        console.error('Failed to load pressure analytics:', err);
        setError(err.message || 'Error loading pressure segment analytics');
      } finally {
        setLoading(false);
      }
    }
    loadPressureData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
        <div className="h-6 bg-white/10 rounded w-48 animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <CardSkeleton rows={6} />
          <CardSkeleton rows={6} />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <ErrorMessage message={error || 'Pressure analytics unavailable'} />
      </div>
    );
  }

  const segments = data.segments || [];

  // Chart data: Deliveries per segment
  const volumeChartData = segments.map((s) => ({
    name: s.segment_name.split('(')[0].trim(),
    fullName: s.segment_name,
    Deliveries: s.total_deliveries,
    LegalBalls: s.legal_balls,
  }));

  // Chart data: Strike Rate vs Economy Rate
  const rateChartData = segments
    .filter((s) => !s.segment_name.includes('Super Over')) // exclude outlier 38-ball super over from main scale
    .map((s) => ({
      name: s.segment_name.split('(')[0].trim(),
      'Batting Strike Rate': s.batting_strike_rate,
      'Bowling Economy': s.bowling_economy,
    }));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* 1. Header */}
      <div className="pb-6 border-b border-white/10">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs font-bold text-[#FFC928] mb-2 font-display">
          <Flame className="w-3.5 h-3.5" />
          <span>Macro Segment Decomposition</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black font-display text-[#F2F4F1] uppercase">
          PRESSURE ANALYTICS & SEGMENTATION
        </h1>
        <p className="text-xs sm:text-sm text-[#A6A9A5] mt-1">
          Rigorous ball-by-ball empirical environment analysis across all 8 regular, pressure, and baseline situations.
        </p>
      </div>

      {/* 2. Mathematical Set Algebra Card */}
      <GlassCard className="p-6 sm:p-8 border-[#FFC928]/30 space-y-4" hover={false}>
        <div className="flex items-center space-x-2 text-[#FFC928]">
          <Layers className="w-5 h-5" />
          <h2 className="text-base sm:text-lg font-bold font-display uppercase tracking-wider text-[#F2F4F1]">
            Mathematical Set Reconciliation & Non-Overlapping Algebra
          </h2>
        </div>

        <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
          {data.note}
        </p>

        {/* Set Formula Visual */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="p-4 rounded-xl bg-black/30 border border-white/10 text-center space-y-1">
            <span className="text-[10px] uppercase font-bold text-[#A6A9A5] font-display">Non-Pressure Baseline</span>
            <div className="text-2xl font-extrabold text-[#F2F4F1] font-mono">147,508</div>
            <span className="text-[10px] text-[#A6A9A5]">73.40% of Regular Play</span>
          </div>

          <div className="p-4 rounded-xl bg-[#FFC928]/10 border border-[#FFC928]/30 text-center space-y-1">
            <span className="text-[10px] uppercase font-bold text-[#FFC928] font-display">Any Pressure (Union)</span>
            <div className="text-2xl font-extrabold text-[#FFC928] font-mono">53,453</div>
            <span className="text-[10px] text-[#A6A9A5]">26.60% Deduplicated Union</span>
          </div>

          <div className="p-4 rounded-xl bg-black/30 border border-white/10 text-center space-y-1">
            <span className="text-[10px] uppercase font-bold text-emerald-400 font-display">Total Regular Innings</span>
            <div className="text-2xl font-extrabold text-emerald-400 font-mono">200,961</div>
            <span className="text-[10px] text-[#A6A9A5]">+38 Quarantined Super Overs</span>
          </div>
        </div>
      </GlassCard>

      {/* 3. Interactive Comparison Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Delivery Volume Chart */}
        <GlassCard className="p-6 space-y-4" hover={false}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm uppercase tracking-wider font-bold text-[#F2F4F1] font-display">
              Delivery Volume by Cricket Environment
            </h3>
            <span className="text-[10px] text-[#A6A9A5]">Ball Counts</span>
          </div>

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={volumeChartData} margin={{ top: 10, right: 10, left: 0, bottom: 40 }}>
                <XAxis dataKey="name" stroke="#A6A9A5" fontSize={10} interval={0} angle={-25} textAnchor="end" />
                <YAxis stroke="#A6A9A5" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1C1D20', borderColor: 'rgba(255,201,40,0.3)', borderRadius: '12px' }}
                  labelStyle={{ color: '#F2F4F1', fontWeight: 'bold' }}
                />
                <Bar dataKey="Deliveries" fill="#FFC928" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Strike Rate vs Economy Chart */}
        <GlassCard className="p-6 space-y-4" hover={false}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm uppercase tracking-wider font-bold text-[#F2F4F1] font-display">
              Batting Strike Rate vs Bowling Economy
            </h3>
            <span className="text-[10px] text-[#A6A9A5]">Rate Metrics</span>
          </div>

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rateChartData} margin={{ top: 10, right: 10, left: 0, bottom: 40 }}>
                <XAxis dataKey="name" stroke="#A6A9A5" fontSize={10} interval={0} angle={-25} textAnchor="end" />
                <YAxis stroke="#A6A9A5" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1C1D20', borderColor: 'rgba(255,201,40,0.3)', borderRadius: '12px' }}
                  labelStyle={{ color: '#F2F4F1', fontWeight: 'bold' }}
                />
                <Legend wrapperStyle={{ paddingTop: '10px' }} />
                <Bar dataKey="Batting Strike Rate" fill="#FFC928" radius={[6, 6, 0, 0]} />
                <Bar dataKey="Bowling Economy" fill="#F2F4F1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* 4. Complete Segment Data Cards Grid */}
      <div className="space-y-4">
        <h3 className="text-lg font-black text-[#F2F4F1] font-display uppercase">
          All 8 Segment Summary Records
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {segments.map((s, idx) => {
            const isSuperOver = s.segment_name.includes('Super Over');
            const isUnion = s.segment_name.includes('Any Pressure');
            return (
              <GlassCard
                key={idx}
                className={`p-5 space-y-3 ${
                  isUnion ? 'border-[#FFC928]/40 shadow-sunshine-sm' : isSuperOver ? 'border-amber-500/30' : ''
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold text-[#A6A9A5]">
                      Segment #{idx + 1}
                    </span>
                    {isSuperOver && (
                      <span className="px-2 py-0.5 rounded bg-amber-500/15 border border-amber-500/30 text-[9px] uppercase font-bold text-amber-300">
                        Quarantined
                      </span>
                    )}
                  </div>
                  <h4 className="text-sm font-extrabold text-[#F2F4F1] font-display mt-0.5">
                    {s.segment_name}
                  </h4>
                </div>

                <div className="space-y-1.5 pt-2 border-t border-white/5 text-xs">
                  <div className="flex justify-between">
                    <span className="text-[#A6A9A5]">Deliveries:</span>
                    <span className="font-mono font-bold text-[#F2F4F1]">{s.total_deliveries.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#A6A9A5]">Strike Rate:</span>
                    <span className="font-mono font-bold text-[#FFC928]">{s.batting_strike_rate}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#A6A9A5]">Economy:</span>
                    <span className="font-mono font-bold text-[#F2F4F1]">{s.bowling_economy}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#A6A9A5]">Dot Ball %:</span>
                    <span className="font-mono text-[#A6A9A5]">{s.overall_dot_percentage}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#A6A9A5]">Boundary Runs %:</span>
                    <span className="font-mono text-[#A6A9A5]">{s.boundary_runs_conceded_pct}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#A6A9A5]">Wickets (Bowler):</span>
                    <span className="font-mono text-[#F2F4F1]">{s.bowler_wickets}</span>
                  </div>
                </div>
              </GlassCard>
            );
          })}
        </div>
      </div>
    </div>
  );
}

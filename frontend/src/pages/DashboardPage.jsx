import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Flame, 
  Trophy, 
  ShieldCheck, 
  Search, 
  ArrowRight, 
  Layers, 
  Zap, 
  Activity, 
  Users, 
  Scale,
  Sparkles,
  BarChart3
} from 'lucide-react';
import api from '../services/api';
import GlassCard from '../components/GlassCard';
import ClutchBadge from '../components/ClutchBadge';
import { CardSkeleton, TableSkeleton } from '../components/LoadingSkeleton';
import ErrorMessage from '../components/ErrorMessage';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [topBatters, setTopBatters] = useState([]);
  const [topBowlers, setTopBowlers] = useState([]);
  const [battingArchetypes, setBattingArchetypes] = useState([]);
  const [bowlingArchetypes, setBowlingArchetypes] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumData, batData, bowlData, batArch, bowlArch] = await Promise.all([
        api.getAnalyticsSummary(),
        api.getBattersLeaderboard({ page: 1, page_size: 5, cohort: 'primary' }),
        api.getBowlersLeaderboard({ page: 1, page_size: 5, cohort: 'primary' }),
        api.getBattingArchetypes(),
        api.getBowlingArchetypes(),
      ]);

      setSummary(sumData);
      setTopBatters(batData.items || []);
      setTopBowlers(bowlData.items || []);
      setBattingArchetypes(batArch || []);
      setBowlingArchetypes(bowlArch || []);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
      setError(err.message || 'Unable to connect to the backend API');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/players?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <ErrorMessage message={error} onRetry={fetchData} />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* 1. Header & Quick Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-white/10">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs font-bold text-[#FFC928] mb-2 font-display">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Cricket Intelligence Platform</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black font-display text-[#F2F4F1] uppercase">
            ANALYTICS DASHBOARD
          </h1>
          <p className="text-xs sm:text-sm text-[#A6A9A5] mt-1">
            Empirical pressure analytics, Bayesian Clutch IQ rankings & K-Means archetypes across 883 T20 matches.
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by player name..."
            className="w-full bg-[#25262A] border border-white/10 rounded-2xl pl-11 pr-4 py-2.5 text-xs sm:text-sm text-[#F2F4F1] placeholder-[#A6A9A5] focus:outline-none focus:border-[#FFC928] transition-colors"
          />
          <Search className="w-4 h-4 text-[#A6A9A5] absolute left-4 top-3" />
        </form>
      </div>

      {/* 2. Key Tournament Statistics Grid */}
      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="glass-panel p-5 rounded-2xl animate-pulse space-y-2">
              <div className="h-4 bg-white/10 rounded w-1/3"></div>
              <div className="h-7 bg-white/20 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <GlassCard className="p-5 space-y-1">
            <div className="flex items-center justify-between text-[#A6A9A5]">
              <span className="text-xs uppercase tracking-wider font-semibold font-display">Total Matches</span>
              <Activity className="w-4 h-4 text-[#FFC928]" />
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-[#F2F4F1] font-mono">
              {summary?.total_matches || '883'}
            </div>
            <div className="text-[11px] text-[#A6A9A5]">
              {summary?.completed_matches || '843'} Completed • {summary?.abandoned_matches || '40'} No Result
            </div>
          </GlassCard>

          <GlassCard className="p-5 space-y-1">
            <div className="flex items-center justify-between text-[#A6A9A5]">
              <span className="text-xs uppercase tracking-wider font-semibold font-display">Regular Deliveries</span>
              <Layers className="w-4 h-4 text-[#FFC928]" />
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-[#F2F4F1] font-mono">
              200,961
            </div>
            <div className="text-[11px] text-[#A6A9A5]">
              +38 Quarantined Super Overs
            </div>
          </GlassCard>

          <GlassCard className="p-5 space-y-1">
            <div className="flex items-center justify-between text-[#A6A9A5]">
              <span className="text-xs uppercase tracking-wider font-semibold font-display">Pressure Ratio</span>
              <Flame className="w-4 h-4 text-[#FFC928]" />
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-[#FFC928] font-mono">
              {summary?.pressure_percentage ? `${summary.pressure_percentage}%` : '26.60%'}
            </div>
            <div className="text-[11px] text-[#A6A9A5]">
              53,453 Deduplicated Pressure Balls
            </div>
          </GlassCard>

          <GlassCard className="p-5 space-y-1">
            <div className="flex items-center justify-between text-[#A6A9A5]">
              <span className="text-xs uppercase tracking-wider font-semibold font-display">Registered Players</span>
              <Users className="w-4 h-4 text-[#FFC928]" />
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-[#F2F4F1] font-mono">
              {summary?.total_batters_count ? '1,217' : '1,217'}
            </div>
            <div className="text-[11px] text-[#A6A9A5]">
              775 Batters • 543 Bowlers in Pressure
            </div>
          </GlassCard>
        </div>
      )}

      {/* 3. Top 5 Batters & Top 5 Bowlers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Batters */}
        <GlassCard className="p-6 space-y-4" hover={false}>
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center space-x-2">
              <Trophy className="w-5 h-5 text-[#FFC928]" />
              <h2 className="text-lg font-bold text-[#F2F4F1] font-display">Top 5 Pressure Batters</h2>
            </div>
            <Link
              to="/leaderboards?tab=batting"
              className="text-xs text-[#FFC928] font-semibold uppercase tracking-wider hover:underline flex items-center space-x-1"
            >
              <span>Full List</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {loading ? (
            <TableSkeleton rows={5} />
          ) : (
            <div className="space-y-2">
              {topBatters.map((player) => (
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
                        SR <span className="text-[#F2F4F1] font-mono">{player.strike_rate}</span> • {player.balls_faced} balls ({player.match_count} matches)
                      </div>
                    </div>
                  </div>
                  <ClutchBadge score={player.clutch_iq} size="sm" showLabel={false} />
                </Link>
              ))}
            </div>
          )}
        </GlassCard>

        {/* Bowlers */}
        <GlassCard className="p-6 space-y-4" hover={false}>
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-[#FFC928]" />
              <h2 className="text-lg font-bold text-[#F2F4F1] font-display">Top 5 Pressure Bowlers</h2>
            </div>
            <Link
              to="/leaderboards?tab=bowling"
              className="text-xs text-[#FFC928] font-semibold uppercase tracking-wider hover:underline flex items-center space-x-1"
            >
              <span>Full List</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {loading ? (
            <TableSkeleton rows={5} />
          ) : (
            <div className="space-y-2">
              {topBowlers.map((player) => (
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
                        Econ <span className="text-[#F2F4F1] font-mono">{player.economy_rate}</span> • {player.bowler_wickets} wkts ({player.legal_balls} balls)
                      </div>
                    </div>
                  </div>
                  <ClutchBadge score={player.clutch_iq} size="sm" showLabel={false} />
                </Link>
              ))}
            </div>
          )}
        </GlassCard>
      </div>

      {/* 4. Archetype Distribution Overview */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xs uppercase tracking-widest text-[#FFC928] font-bold font-display">
              Unsupervised Clustering (K=3)
            </h2>
            <h3 className="text-xl sm:text-2xl font-black text-[#F2F4F1] font-display">
              PLAYER ARCHETYPES
            </h3>
          </div>
          <Link
            to="/archetypes"
            className="text-xs text-[#FFC928] font-semibold uppercase tracking-wider hover:underline flex items-center space-x-1"
          >
            <span>Explore All 6 Archetypes</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Batting Archetypes summary */}
          <GlassCard className="p-5 space-y-3">
            <h4 className="text-xs uppercase tracking-wider font-bold text-[#FFC928] font-display">
              Batting Personas (775 Batters)
            </h4>
            <div className="space-y-2">
              {battingArchetypes.map((arch) => (
                <Link
                  key={arch.cluster_id}
                  to={`/archetypes?tab=batting&cluster=${arch.cluster_id}`}
                  className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 transition-colors"
                >
                  <div>
                    <div className="text-xs sm:text-sm font-bold text-[#F2F4F1]">{arch.archetype_name}</div>
                    <div className="text-[11px] text-[#A6A9A5]">
                      Mean SR: <span className="text-[#F2F4F1] font-mono">{arch.mean_pressure_strike_rate}</span> • Dot: {arch.mean_dot_ball_pct}%
                    </div>
                  </div>
                  <span className="text-xs font-mono font-bold text-[#FFC928] px-2.5 py-1 rounded-lg bg-[#FFC928]/10">
                    {arch.total_player_count} Players
                  </span>
                </Link>
              ))}
            </div>
          </GlassCard>

          {/* Bowling Archetypes summary */}
          <GlassCard className="p-5 space-y-3">
            <h4 className="text-xs uppercase tracking-wider font-bold text-[#FFC928] font-display">
              Bowling Personas (543 Bowlers)
            </h4>
            <div className="space-y-2">
              {bowlingArchetypes.map((arch) => (
                <Link
                  key={arch.cluster_id}
                  to={`/archetypes?tab=bowling&cluster=${arch.cluster_id}`}
                  className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 transition-colors"
                >
                  <div>
                    <div className="text-xs sm:text-sm font-bold text-[#F2F4F1]">{arch.archetype_name}</div>
                    <div className="text-[11px] text-[#A6A9A5]">
                      Mean Econ: <span className="text-[#F2F4F1] font-mono">{arch.mean_pressure_economy}</span> • Dot: {arch.mean_dot_ball_pct}%
                    </div>
                  </div>
                  <span className="text-xs font-mono font-bold text-[#FFC928] px-2.5 py-1 rounded-lg bg-[#FFC928]/10">
                    {arch.total_player_count} Players
                  </span>
                </Link>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>

      {/* 5. Navigation Shortcuts Banner */}
      <GlassCard className="p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-6 border-[#FFC928]/30">
        <div className="space-y-1 text-center md:text-left">
          <h3 className="text-lg font-bold text-[#F2F4F1] font-display">
            Compare Head-to-Head Records Under Pressure
          </h3>
          <p className="text-xs text-[#A6A9A5] max-w-lg">
            Evaluate between 2 and 5 players side-by-side on strike rate, boundary rate, economy rate, and credibility-shrunk Clutch IQ.
          </p>
        </div>
        <Link
          to="/compare"
          className="px-6 py-3 rounded-xl bg-[#FFC928] text-[#1C1D20] text-xs font-bold uppercase tracking-wider shadow-sunshine-sm hover:scale-[1.02] transition-transform whitespace-nowrap"
        >
          Launch Player Comparison
        </Link>
      </GlassCard>
    </div>
  );
}

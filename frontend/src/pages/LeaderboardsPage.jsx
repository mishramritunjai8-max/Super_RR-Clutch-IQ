import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { 
  Trophy, 
  ShieldCheck, 
  Search, 
  ArrowUpDown, 
  ChevronLeft, 
  ChevronRight, 
  SlidersHorizontal,
  Flame,
  ArrowRight
} from 'lucide-react';
import api from '../services/api';
import GlassCard from '../components/GlassCard';
import ClutchBadge from '../components/ClutchBadge';
import { TableSkeleton } from '../components/LoadingSkeleton';
import ErrorMessage from '../components/ErrorMessage';

export default function LeaderboardsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTab = searchParams.get('tab') === 'bowling' ? 'bowling' : 'batting';
  const [activeTab, setActiveTab] = useState(initialTab);

  // Filter States
  const [cohort, setCohort] = useState('primary'); // 'primary', 'emerging', 'all'
  const [search, setSearch] = useState('');
  const [minBalls, setMinBalls] = useState('');
  const [sortBy, setSortBy] = useState('clutch_iq');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // Data States
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLeaderboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        page_size: pageSize,
        cohort,
        sort_by: sortBy,
        sort_order: sortOrder,
        search: search.trim() || undefined,
        min_balls: minBalls ? parseInt(minBalls, 10) : undefined,
      };

      const res = activeTab === 'batting'
        ? await api.getBattersLeaderboard(params)
        : await api.getBowlersLeaderboard(params);

      setData(res);
    } catch (err) {
      console.error('Failed to fetch leaderboard:', err);
      setError(err.message || 'Error loading leaderboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaderboard();
  }, [activeTab, cohort, sortBy, sortOrder, page, pageSize]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchLeaderboard();
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setSearchParams({ tab });
    setPage(1);
    setSortBy('clutch_iq');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* 1. Header & Tab Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs font-bold text-[#FFC928] mb-2 font-display">
            <Trophy className="w-3.5 h-3.5" />
            <span>Bayesian Credibility Rankings</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black font-display text-[#F2F4F1] uppercase">
            CLUTCH IQ LEADERBOARDS
          </h1>
          <p className="text-xs sm:text-sm text-[#A6A9A5] mt-1">
            Empirical pressure rankings shrunk against personal baselines using empirical Bayes weights.
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="inline-flex p-1 rounded-2xl bg-[#25262A] border border-white/10">
          <button
            onClick={() => handleTabChange('batting')}
            className={`px-5 py-2 rounded-xl text-xs sm:text-sm font-bold uppercase tracking-wider transition-all flex items-center space-x-2 ${
              activeTab === 'batting'
                ? 'bg-[#FFC928] text-[#1C1D20] shadow-sunshine-sm'
                : 'text-[#A6A9A5] hover:text-[#F2F4F1]'
            }`}
          >
            <Trophy className="w-4 h-4" />
            <span>Batting</span>
          </button>
          <button
            onClick={() => handleTabChange('bowling')}
            className={`px-5 py-2 rounded-xl text-xs sm:text-sm font-bold uppercase tracking-wider transition-all flex items-center space-x-2 ${
              activeTab === 'bowling'
                ? 'bg-[#FFC928] text-[#1C1D20] shadow-sunshine-sm'
                : 'text-[#A6A9A5] hover:text-[#F2F4F1]'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Bowling</span>
          </button>
        </div>
      </div>

      {/* 2. Controls & Filter Bar */}
      <GlassCard className="p-4 sm:p-5 space-y-4" hover={false}>
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
          {/* Cohort Selector */}
          <div className="md:col-span-4 flex items-center space-x-1.5 p-1 rounded-xl bg-black/20 border border-white/5">
            {[
              { id: 'primary', label: 'Primary (≥50 Balls)' },
              { id: 'emerging', label: 'Emerging (<50 Balls)' },
              { id: 'all', label: 'All Players' },
            ].map((c) => (
              <button
                key={c.id}
                onClick={() => { setCohort(c.id); setPage(1); }}
                className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold tracking-tight transition-all ${
                  cohort === c.id
                    ? 'bg-[#FFC928]/20 text-[#FFC928] border border-[#FFC928]/40'
                    : 'text-[#A6A9A5] hover:text-[#F2F4F1]'
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>

          {/* Player Search Input */}
          <form onSubmit={handleSearchSubmit} className="md:col-span-4 relative">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter by player name..."
              className="w-full bg-[#1C1D20] border border-white/10 rounded-xl pl-9 pr-4 py-2 text-xs text-[#F2F4F1] placeholder-[#A6A9A5] focus:outline-none focus:border-[#FFC928]"
            />
            <Search className="w-3.5 h-3.5 text-[#A6A9A5] absolute left-3 top-3" />
          </form>

          {/* Sort By Field */}
          <div className="md:col-span-3 flex items-center space-x-2">
            <select
              value={sortBy}
              onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
              className="w-full bg-[#1C1D20] border border-white/10 rounded-xl px-3 py-2 text-xs text-[#F2F4F1] focus:outline-none focus:border-[#FFC928]"
            >
              <option value="clutch_iq">Sort by: Clutch IQ Score</option>
              {activeTab === 'batting' ? (
                <>
                  <option value="strike_rate">Sort by: Strike Rate</option>
                  <option value="balls_faced">Sort by: Balls Faced</option>
                  <option value="total_runs">Sort by: Total Runs</option>
                  <option value="batting_average">Sort by: Batting Average</option>
                  <option value="boundary_ball_pct">Sort by: Boundary %</option>
                  <option value="dot_ball_pct">Sort by: Dot Ball %</option>
                </>
              ) : (
                <>
                  <option value="economy_rate">Sort by: Economy Rate</option>
                  <option value="legal_balls">Sort by: Legal Balls</option>
                  <option value="bowler_wickets">Sort by: Bowler Wickets</option>
                  <option value="bowling_strike_rate">Sort by: Bowling Strike Rate</option>
                  <option value="bowling_average">Sort by: Bowling Average</option>
                  <option value="dot_ball_pct">Sort by: Dot Ball %</option>
                </>
              )}
            </select>

            <button
              onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
              className="p-2 rounded-xl bg-white/5 border border-white/10 text-[#A6A9A5] hover:text-[#F2F4F1] transition-colors"
              title={`Switch to ${sortOrder === 'desc' ? 'Ascending' : 'Descending'}`}
            >
              <ArrowUpDown className="w-4 h-4" />
            </button>
          </div>

          {/* Minimum Balls Filter */}
          <div className="md:col-span-1">
            <input
              type="number"
              value={minBalls}
              onChange={(e) => setMinBalls(e.target.value)}
              onBlur={() => { setPage(1); fetchLeaderboard(); }}
              placeholder="Min balls"
              className="w-full bg-[#1C1D20] border border-white/10 rounded-xl px-2.5 py-2 text-xs text-[#F2F4F1] placeholder-[#A6A9A5] focus:outline-none focus:border-[#FFC928]"
            />
          </div>
        </div>
      </GlassCard>

      {/* 3. Leaderboard Table View */}
      {loading ? (
        <TableSkeleton rows={10} />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchLeaderboard} />
      ) : data?.items?.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center text-[#A6A9A5]">
          No players match the selected filters or search criteria.
        </div>
      ) : (
        <div className="glass-panel rounded-2xl overflow-hidden border border-white/10">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-[#25262A]/90 text-[#A6A9A5] uppercase text-[10px] tracking-wider border-b border-white/10 font-display">
                <tr>
                  <th className="py-3.5 px-4 w-12 text-center">Rank</th>
                  <th className="py-3.5 px-4">Player</th>
                  <th className="py-3.5 px-4">Archetype</th>
                  {activeTab === 'batting' ? (
                    <>
                      <th className="py-3.5 px-3 text-right">Balls</th>
                      <th className="py-3.5 px-3 text-right">Runs</th>
                      <th className="py-3.5 px-3 text-right">SR</th>
                      <th className="py-3.5 px-3 text-right">Avg</th>
                      <th className="py-3.5 px-3 text-right">Dot %</th>
                      <th className="py-3.5 px-3 text-right">Bound %</th>
                      <th className="py-3.5 px-3 text-right">Δ SR</th>
                    </>
                  ) : (
                    <>
                      <th className="py-3.5 px-3 text-right">Balls</th>
                      <th className="py-3.5 px-3 text-right">Runs</th>
                      <th className="py-3.5 px-3 text-right">Wkts</th>
                      <th className="py-3.5 px-3 text-right">Econ</th>
                      <th className="py-3.5 px-3 text-right">SR</th>
                      <th className="py-3.5 px-3 text-right">Dot %</th>
                      <th className="py-3.5 px-3 text-right">Δ Econ</th>
                    </>
                  )}
                  <th className="py-3.5 px-4 text-center">Clutch IQ</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {data.items.map((player) => (
                  <tr
                    key={player.player_id}
                    className="hover:bg-white/[0.04] transition-colors group"
                  >
                    {/* Rank */}
                    <td className="py-3.5 px-4 text-center font-mono font-bold text-[#A6A9A5]">
                      {player.rank ? (
                        <span className={`inline-block px-2 py-0.5 rounded ${
                          player.rank <= 3
                            ? 'bg-[#FFC928]/20 text-[#FFC928] border border-[#FFC928]/30 font-black'
                            : 'text-[#F2F4F1]'
                        }`}>
                          #{player.rank}
                        </span>
                      ) : (
                        <span className="text-[11px] text-[#A6A9A5]">—</span>
                      )}
                    </td>

                    {/* Player Name */}
                    <td className="py-3.5 px-4">
                      <Link
                        to={`/players/${player.player_id}`}
                        className="font-bold text-[#F2F4F1] hover:text-[#FFC928] transition-colors flex items-center space-x-1.5"
                      >
                        <span>{player.player_name}</span>
                        <ArrowRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity text-[#FFC928]" />
                      </Link>
                      <span className="text-[10px] text-[#A6A9A5] block">
                        {player.match_count} matches • ID: {player.player_id}
                      </span>
                    </td>

                    {/* Archetype */}
                    <td className="py-3.5 px-4">
                      <span className="inline-block px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-[11px] text-[#F2F4F1] max-w-[200px] truncate" title={player.archetype_name}>
                        {player.archetype_name}
                      </span>
                    </td>

                    {/* Dynamic Metrics */}
                    {activeTab === 'batting' ? (
                      <>
                        <td className="py-3.5 px-3 text-right font-mono text-[#F2F4F1]">{player.balls_faced}</td>
                        <td className="py-3.5 px-3 text-right font-mono text-[#F2F4F1]">{player.total_runs}</td>
                        <td className="py-3.5 px-3 text-right font-mono font-bold text-[#FFC928]">{player.strike_rate}</td>
                        <td className="py-3.5 px-3 text-right font-mono text-[#A6A9A5]">{player.batting_average ?? '—'}</td>
                        <td className="py-3.5 px-3 text-right font-mono text-[#A6A9A5]">{player.dot_ball_pct}%</td>
                        <td className="py-3.5 px-3 text-right font-mono text-[#A6A9A5]">{player.boundary_ball_pct}%</td>
                        <td className={`py-3.5 px-3 text-right font-mono font-medium ${player.raw_delta_strike_rate >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {player.raw_delta_strike_rate > 0 ? `+${player.raw_delta_strike_rate}` : player.raw_delta_strike_rate}
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="py-3.5 px-3 text-right font-mono text-[#F2F4F1]">{player.legal_balls}</td>
                        <td className="py-3.5 px-3 text-right font-mono text-[#F2F4F1]">{player.runs_conceded}</td>
                        <td className="py-3.5 px-3 text-right font-mono font-bold text-[#F2F4F1]">{player.bowler_wickets}</td>
                        <td className="py-3.5 px-3 text-right font-mono font-bold text-[#FFC928]">{player.economy_rate}</td>
                        <td className="py-3.5 px-3 text-right font-mono text-[#A6A9A5]">{player.bowling_strike_rate ?? '—'}</td>
                        <td className="py-3.5 px-3 text-right font-mono text-[#A6A9A5]">{player.dot_ball_pct}%</td>
                        <td className={`py-3.5 px-3 text-right font-mono font-medium ${player.raw_delta_economy >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {player.raw_delta_economy > 0 ? `+${player.raw_delta_economy}` : player.raw_delta_economy}
                        </td>
                      </>
                    )}

                    {/* Clutch IQ Badge */}
                    <td className="py-3.5 px-4 text-center">
                      <ClutchBadge
                        score={player.clutch_iq}
                        cohort={player.cohort}
                        size="sm"
                        showLabel={false}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 4. Pagination Footer */}
          {data?.pagination && (
            <div className="bg-[#25262A]/60 px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-white/10 text-xs text-[#A6A9A5]">
              <div>
                Showing <span className="font-mono text-[#F2F4F1]">{((page - 1) * pageSize) + 1}</span> to{' '}
                <span className="font-mono text-[#F2F4F1]">{Math.min(page * pageSize, data.pagination.total_records)}</span> of{' '}
                <span className="font-mono text-[#F2F4F1]">{data.pagination.total_records}</span> players
              </div>

              <div className="flex items-center space-x-2">
                <button
                  disabled={!data.pagination.has_prev}
                  onClick={() => setPage(page - 1)}
                  className="p-1.5 rounded-lg bg-white/5 border border-white/10 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/10 text-[#F2F4F1] transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="px-3 py-1 font-mono text-[#F2F4F1] bg-white/5 rounded-lg border border-white/10">
                  {page} / {data.pagination.total_pages}
                </span>
                <button
                  disabled={!data.pagination.has_next}
                  onClick={() => setPage(page + 1)}
                  className="p-1.5 rounded-lg bg-white/5 border border-white/10 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/10 text-[#F2F4F1] transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

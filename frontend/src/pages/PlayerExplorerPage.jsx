import React, { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Users, 
  Search, 
  Filter, 
  ArrowRight, 
  ShieldCheck, 
  Trophy, 
  Sparkles,
  Scale
} from 'lucide-react';
import api from '../services/api';
import GlassCard from '../components/GlassCard';
import ClutchBadge from '../components/ClutchBadge';
import { CardSkeleton } from '../components/LoadingSkeleton';
import ErrorMessage from '../components/ErrorMessage';

export default function PlayerExplorerPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const initialSearch = searchParams.get('search') || '';

  const [search, setSearch] = useState(initialSearch);
  const [roleFilter, setRoleFilter] = useState('all'); // 'all', 'all_rounders', 'batters', 'bowlers'
  const [cohortFilter, setCohortFilter] = useState('all'); // 'all', 'primary', 'emerging'
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // We load players from the leaderboards or search directly
  const fetchPlayers = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch batters and bowlers concurrently to merge player views
      const [battersRes, bowlersRes] = await Promise.all([
        api.getBattersLeaderboard({
          page: 1,
          page_size: 100,
          cohort: cohortFilter !== 'all' ? cohortFilter : undefined,
          search: search.trim() || undefined,
        }),
        api.getBowlersLeaderboard({
          page: 1,
          page_size: 100,
          cohort: cohortFilter !== 'all' ? cohortFilter : undefined,
          search: search.trim() || undefined,
        }),
      ]);

      // Merge by player_id
      const playerMap = new Map();

      (battersRes.items || []).forEach((b) => {
        playerMap.set(b.player_id, {
          player_id: b.player_id,
          player_name: b.player_name,
          batting: b,
          bowling: null,
          has_batting: true,
          has_bowling: false,
        });
      });

      (bowlersRes.items || []).forEach((w) => {
        if (playerMap.has(w.player_id)) {
          const existing = playerMap.get(w.player_id);
          existing.bowling = w;
          existing.has_bowling = true;
        } else {
          playerMap.set(w.player_id, {
            player_id: w.player_id,
            player_name: w.player_name,
            batting: null,
            bowling: w,
            has_batting: false,
            has_bowling: true,
          });
        }
      });

      let merged = Array.from(playerMap.values());

      // Filter by role
      if (roleFilter === 'all_rounders') {
        merged = merged.filter((p) => p.has_batting && p.has_bowling);
      } else if (roleFilter === 'batters') {
        merged = merged.filter((p) => p.has_batting && !p.has_bowling);
      } else if (roleFilter === 'bowlers') {
        merged = merged.filter((p) => !p.has_batting && p.has_bowling);
      }

      setPlayers(merged);
    } catch (err) {
      console.error('Failed to load players:', err);
      setError(err.message || 'Error fetching player catalog');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlayers();
  }, [roleFilter, cohortFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setSearchParams(search ? { search } : {});
    fetchPlayers();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs font-bold text-[#FFC928] mb-2 font-display">
            <Users className="w-3.5 h-3.5" />
            <span>Complete Player Discovery</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black font-display text-[#F2F4F1] uppercase">
            PLAYER EXPLORER
          </h1>
          <p className="text-xs sm:text-sm text-[#A6A9A5] mt-1">
            Browse registered T20 players, inspect role availability, and launch side-by-side comparisons.
          </p>
        </div>

        <Link
          to="/compare"
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10 text-xs font-bold uppercase tracking-wider text-[#F2F4F1] transition-all"
        >
          <Scale className="w-4 h-4 text-[#FFC928]" />
          <span>Compare Players</span>
        </Link>
      </div>

      {/* 2. Search & Filters */}
      <GlassCard className="p-4 sm:p-5 space-y-4" hover={false}>
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
          {/* Search Form */}
          <form onSubmit={handleSearchSubmit} className="md:col-span-5 relative">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by player name or ID..."
              className="w-full bg-[#1C1D20] border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-xs sm:text-sm text-[#F2F4F1] placeholder-[#A6A9A5] focus:outline-none focus:border-[#FFC928]"
            />
            <Search className="w-4 h-4 text-[#A6A9A5] absolute left-3.5 top-3" />
          </form>

          {/* Role Filter Buttons */}
          <div className="md:col-span-4 flex items-center space-x-1.5 p-1 rounded-xl bg-black/20 border border-white/5">
            {[
              { id: 'all', label: 'All' },
              { id: 'all_rounders', label: 'All-Rounders' },
              { id: 'batters', label: 'Batters' },
              { id: 'bowlers', label: 'Bowlers' },
            ].map((rf) => (
              <button
                key={rf.id}
                onClick={() => setRoleFilter(rf.id)}
                className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold tracking-tight transition-all ${
                  roleFilter === rf.id
                    ? 'bg-[#FFC928]/20 text-[#FFC928] border border-[#FFC928]/40'
                    : 'text-[#A6A9A5] hover:text-[#F2F4F1]'
                }`}
              >
                {rf.label}
              </button>
            ))}
          </div>

          {/* Cohort Filter */}
          <div className="md:col-span-3 flex items-center space-x-1.5 p-1 rounded-xl bg-black/20 border border-white/5">
            {[
              { id: 'all', label: 'All Cohorts' },
              { id: 'primary', label: 'Primary (≥50)' },
              { id: 'emerging', label: 'Emerging' },
            ].map((cf) => (
              <button
                key={cf.id}
                onClick={() => setCohortFilter(cf.id)}
                className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold tracking-tight transition-all ${
                  cohortFilter === cf.id
                    ? 'bg-[#FFC928]/20 text-[#FFC928] border border-[#FFC928]/40'
                    : 'text-[#A6A9A5] hover:text-[#F2F4F1]'
                }`}
              >
                {cf.label}
              </button>
            ))}
          </div>
        </div>
      </GlassCard>

      {/* 3. Player Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} rows={4} />
          ))}
        </div>
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchPlayers} />
      ) : players.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center text-[#A6A9A5]">
          No players found matching your criteria. Try adjusting the search query or filters.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {players.map((p) => {
            const hasBoth = p.has_batting && p.has_bowling;
            return (
              <GlassCard key={p.player_id} className="p-6 flex flex-col justify-between space-y-4">
                {/* Header */}
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="text-base font-extrabold text-[#F2F4F1] font-display hover:text-[#FFC928] transition-colors">
                        <Link to={`/players/${p.player_id}`}>{p.player_name}</Link>
                      </h3>
                      <span className="text-[11px] font-mono text-[#A6A9A5]">
                        Player ID: {p.player_id}
                      </span>
                    </div>

                    {/* Role tag */}
                    <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[10px] uppercase tracking-wider text-[#A6A9A5] font-semibold">
                      {hasBoth ? 'All-Rounder' : p.has_batting ? 'Batter' : 'Bowler'}
                    </span>
                  </div>

                  {/* Archetype display */}
                  <div className="space-y-1 pt-1">
                    {p.batting && (
                      <div className="text-[11px] text-[#A6A9A5] truncate" title={p.batting.archetype_name}>
                        <span className="text-[#FFC928] font-semibold">Bat:</span> {p.batting.archetype_name}
                      </div>
                    )}
                    {p.bowling && (
                      <div className="text-[11px] text-[#A6A9A5] truncate" title={p.bowling.archetype_name}>
                        <span className="text-[#FFC928] font-semibold">Bowl:</span> {p.bowling.archetype_name}
                      </div>
                    )}
                  </div>
                </div>

                {/* Clutch Scores Bar */}
                <div className="pt-3 border-t border-white/10 flex items-center justify-between">
                  <div className="space-y-1">
                    {p.batting && (
                      <div className="flex items-center space-x-2">
                        <span className="text-[10px] uppercase tracking-wider text-[#A6A9A5] w-10">Bat IQ</span>
                        <ClutchBadge score={p.batting.clutch_iq} rank={p.batting.rank} cohort={p.batting.cohort} size="sm" showLabel={false} />
                      </div>
                    )}
                    {p.bowling && (
                      <div className="flex items-center space-x-2">
                        <span className="text-[10px] uppercase tracking-wider text-[#A6A9A5] w-10">Bowl IQ</span>
                        <ClutchBadge score={p.bowling.clutch_iq} rank={p.bowling.rank} cohort={p.bowling.cohort} size="sm" showLabel={false} />
                      </div>
                    )}
                  </div>

                  {/* Profile Action Link */}
                  <Link
                    to={`/players/${p.player_id}`}
                    className="p-2 rounded-xl bg-white/5 hover:bg-[#FFC928]/20 border border-white/10 hover:border-[#FFC928]/40 text-[#F2F4F1] hover:text-[#FFC928] transition-all"
                    title="View Comprehensive Player Profile"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </GlassCard>
            );
          })}
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  Binary, 
  Trophy, 
  ShieldCheck, 
  Users, 
  Sparkles, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  ArrowRight,
  Info
} from 'lucide-react';
import api from '../services/api';
import GlassCard from '../components/GlassCard';
import ClutchBadge from '../components/ClutchBadge';
import { CardSkeleton, TableSkeleton } from '../components/LoadingSkeleton';
import ErrorMessage from '../components/ErrorMessage';

export default function ArchetypesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTab = searchParams.get('tab') === 'bowling' ? 'bowling' : 'batting';
  const initialCluster = searchParams.get('cluster') ? parseInt(searchParams.get('cluster'), 10) : 0;

  const [activeTab, setActiveTab] = useState(initialTab);
  const [selectedCluster, setSelectedCluster] = useState(initialCluster);

  const [archetypesList, setArchetypesList] = useState([]);
  const [clusterDetail, setClusterDetail] = useState(null);
  const [page, setPage] = useState(1);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState(null);

  // Load Archetypes List for active tab
  useEffect(() => {
    async function loadArchetypes() {
      setLoadingList(true);
      setError(null);
      try {
        const list = activeTab === 'batting'
          ? await api.getBattingArchetypes()
          : await api.getBowlingArchetypes();
        setArchetypesList(list || []);

        // Ensure selected cluster is valid
        if (list && list.length > 0) {
          const validCluster = list.some((a) => a.cluster_id === selectedCluster)
            ? selectedCluster
            : list[0].cluster_id;
          setSelectedCluster(validCluster);
        }
      } catch (err) {
        console.error('Failed to load archetypes list:', err);
        setError(err.message || 'Error loading archetypes');
      } finally {
        setLoadingList(false);
      }
    }
    loadArchetypes();
  }, [activeTab]);

  // Load Selected Cluster Detail & Assigned Roster
  useEffect(() => {
    if (selectedCluster === null || selectedCluster === undefined) return;
    async function loadDetail() {
      setLoadingDetail(true);
      try {
        const detail = activeTab === 'batting'
          ? await api.getBattingArchetypeDetail(selectedCluster, { page, page_size: 15 })
          : await api.getBowlingArchetypeDetail(selectedCluster, { page, page_size: 15 });
        setClusterDetail(detail);
      } catch (err) {
        console.error('Failed to load cluster detail:', err);
      } finally {
        setLoadingDetail(false);
      }
    }
    loadDetail();
  }, [activeTab, selectedCluster, page]);

  const handleTabSwitch = (tab) => {
    setActiveTab(tab);
    setSearchParams({ tab, cluster: 0 });
    setSelectedCluster(0);
    setPage(1);
  };

  const handleClusterSelect = (cid) => {
    setSelectedCluster(cid);
    setSearchParams({ tab: activeTab, cluster: cid });
    setPage(1);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* 1. Header & Tab Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs font-bold text-[#FFC928] mb-2 font-display">
            <Binary className="w-3.5 h-3.5" />
            <span>Phase 4 Machine Learning Personas</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black font-display text-[#F2F4F1] uppercase">
            PLAYER ARCHETYPES
          </h1>
          <p className="text-xs sm:text-sm text-[#A6A9A5] mt-1">
            Empirical behavioral personas discovered via K-Means clustering ($K=3$).
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="inline-flex p-1 rounded-2xl bg-[#25262A] border border-white/10">
          <button
            onClick={() => handleTabSwitch('batting')}
            className={`px-5 py-2 rounded-xl text-xs sm:text-sm font-bold uppercase tracking-wider transition-all flex items-center space-x-2 ${
              activeTab === 'batting'
                ? 'bg-[#FFC928] text-[#1C1D20] shadow-sunshine-sm'
                : 'text-[#A6A9A5] hover:text-[#F2F4F1]'
            }`}
          >
            <Trophy className="w-4 h-4" />
            <span>Batting Archetypes (3)</span>
          </button>
          <button
            onClick={() => handleTabSwitch('bowling')}
            className={`px-5 py-2 rounded-xl text-xs sm:text-sm font-bold uppercase tracking-wider transition-all flex items-center space-x-2 ${
              activeTab === 'bowling'
                ? 'bg-[#FFC928] text-[#1C1D20] shadow-sunshine-sm'
                : 'text-[#A6A9A5] hover:text-[#F2F4F1]'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Bowling Archetypes (3)</span>
          </button>
        </div>
      </div>

      {/* 2. Critical Methodological Note */}
      <div className="glass-panel rounded-2xl p-4 flex items-start space-x-3 text-xs text-[#A6A9A5] border-amber-500/20">
        <Info className="w-5 h-5 text-[#FFC928] shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong className="text-[#F2F4F1]">Statistical Classification Note:</strong> Archetypes represent empirical playing styles, <em>not</em> quality rankings. Primary cohort players were fitted directly in scikit-learn ($K=3$), while emerging cohort players with $&lt; 50$ balls are provisionally assigned via nearest centroid Euclidean distance.
        </p>
      </div>

      {/* 3. Archetype Cards Grid */}
      {loadingList ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <CardSkeleton key={i} rows={4} />
          ))}
        </div>
      ) : error ? (
        <ErrorMessage message={error} onRetry={() => handleTabSwitch(activeTab)} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {archetypesList.map((arch) => {
            const isSelected = arch.cluster_id === selectedCluster;
            return (
              <GlassCard
                key={arch.cluster_id}
                onClick={() => handleClusterSelect(arch.cluster_id)}
                className={`p-6 cursor-pointer space-y-4 text-left transition-all relative ${
                  isSelected
                    ? 'border-[#FFC928] shadow-sunshine-md bg-white/[0.07]'
                    : 'hover:border-white/20'
                }`}
              >
                {/* Cluster Tag & Count */}
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-1 rounded-md bg-[#FFC928]/15 border border-[#FFC928]/30 font-mono text-xs font-bold text-[#FFC928]">
                    Cluster #{arch.cluster_id}
                  </span>
                  <span className="text-xs text-[#A6A9A5] font-mono">
                    <strong className="text-[#F2F4F1]">{arch.total_player_count}</strong> Players
                  </span>
                </div>

                {/* Name */}
                <h3 className="text-base sm:text-lg font-black font-display text-[#F2F4F1]">
                  {arch.archetype_name}
                </h3>

                {/* Key Centroid Metric */}
                <div className="p-3 rounded-xl bg-black/20 border border-white/5 space-y-1 text-xs">
                  {activeTab === 'batting' ? (
                    <>
                      <div className="flex justify-between">
                        <span className="text-[#A6A9A5]">Mean Strike Rate:</span>
                        <span className="font-mono font-bold text-[#FFC928]">{arch.mean_pressure_strike_rate}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#A6A9A5]">Mean Dot %:</span>
                        <span className="font-mono text-[#F2F4F1]">{arch.mean_dot_ball_pct}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#A6A9A5]">Mean Boundary %:</span>
                        <span className="font-mono text-[#F2F4F1]">{arch.mean_boundary_ball_pct}%</span>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex justify-between">
                        <span className="text-[#A6A9A5]">Mean Economy:</span>
                        <span className="font-mono font-bold text-[#FFC928]">{arch.mean_pressure_economy}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#A6A9A5]">Mean Dot %:</span>
                        <span className="font-mono text-[#F2F4F1]">{arch.mean_dot_ball_pct}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#A6A9A5]">Boundaries Conceded:</span>
                        <span className="font-mono text-[#F2F4F1]">{arch.mean_boundary_balls_per_100}/100</span>
                      </div>
                    </>
                  )}
                </div>

                {/* Cohort Breakdown */}
                <div className="text-[11px] text-[#A6A9A5] flex justify-between">
                  <span>Primary: <strong className="text-[#F2F4F1] font-mono">{arch.primary_player_count}</strong></span>
                  <span>Emerging (Prov): <strong className="text-amber-400 font-mono">{arch.emerging_player_count}</strong></span>
                </div>
              </GlassCard>
            );
          })}
        </div>
      )}

      {/* 4. Deep Cluster Detail & Assigned Player Roster */}
      {clusterDetail && (
        <div className="space-y-6 pt-4">
          <GlassCard className="p-6 sm:p-8 space-y-6" hover={false}>
            {/* Header */}
            <div className="space-y-2 pb-6 border-b border-white/10">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-md bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs font-bold text-[#FFC928]">
                <span>Selected Persona #{clusterDetail.profile.cluster_id}</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-black font-display text-[#F2F4F1]">
                {clusterDetail.profile.archetype_name}
              </h2>
              <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed">
                {clusterDetail.profile.distinguishing_characteristics}
              </p>
            </div>

            {/* Strengths & Weaknesses Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-2">
                <div className="flex items-center space-x-2 text-emerald-400 font-bold text-xs uppercase tracking-wider font-display">
                  <CheckCircle className="w-4 h-4" />
                  <span>Empirical Performance Strengths</span>
                </div>
                <p className="text-xs text-[#A6A9A5] leading-relaxed">
                  {clusterDetail.profile.strengths}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-rose-500/5 border border-rose-500/20 space-y-2">
                <div className="flex items-center space-x-2 text-rose-400 font-bold text-xs uppercase tracking-wider font-display">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Performance Vulnerabilities & Blind Spots</span>
                </div>
                <p className="text-xs text-[#A6A9A5] leading-relaxed">
                  {clusterDetail.profile.weaknesses}
                </p>
              </div>
            </div>

            {/* Tactical Scouting Recommendation */}
            <div className="p-4 rounded-xl bg-[#FFC928]/5 border border-[#FFC928]/20 space-y-1">
              <span className="text-[10px] uppercase tracking-widest text-[#FFC928] font-bold font-display">
                Tactical Scouting & Squad Utility
              </span>
              <p className="text-xs text-[#F2F4F1] leading-relaxed">
                {clusterDetail.profile.potential_tactical_role}
              </p>
            </div>

            {/* Representative Players */}
            {clusterDetail.profile.representative_players && clusterDetail.profile.representative_players.length > 0 && (
              <div className="pt-2">
                <span className="text-xs uppercase tracking-wider text-[#A6A9A5] font-semibold block mb-2 font-display">
                  Notable Representative Players in this Cluster:
                </span>
                <div className="flex flex-wrap gap-2">
                  {clusterDetail.profile.representative_players.map((name, i) => (
                    <span key={i} className="px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-xs font-semibold text-[#F2F4F1]">
                      {name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </GlassCard>

          {/* Assigned Player Roster Table */}
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-[#F2F4F1] font-display flex items-center justify-between">
              <span>Assigned Players Roster (Sorted by Clutch IQ)</span>
              <span className="text-xs font-mono text-[#A6A9A5]">
                {clusterDetail.players?.pagination?.total_records || 0} Total Players Assigned
              </span>
            </h3>

            {loadingDetail ? (
              <TableSkeleton rows={6} />
            ) : clusterDetail.players?.items?.length > 0 ? (
              <div className="glass-panel rounded-2xl overflow-hidden border border-white/10">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs sm:text-sm">
                    <thead className="bg-[#25262A]/90 text-[#A6A9A5] uppercase text-[10px] tracking-wider border-b border-white/10 font-display">
                      <tr>
                        <th className="py-3 px-4 w-12 text-center">Rank</th>
                        <th className="py-3 px-4">Player</th>
                        <th className="py-3 px-4">Cohort</th>
                        <th className="py-3 px-4 text-right">Balls</th>
                        <th className="py-3 px-4 text-right">Matches</th>
                        <th className="py-3 px-4 text-right">{activeTab === 'batting' ? 'Strike Rate' : 'Economy'}</th>
                        <th className="py-3 px-4 text-center">Clutch IQ</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 font-mono text-xs">
                      {clusterDetail.players.items.map((player) => (
                        <tr key={player.player_id} className="hover:bg-white/[0.04] transition-colors">
                          <td className="py-3 px-4 text-center text-[#A6A9A5]">
                            {player.rank ? `#${player.rank}` : '—'}
                          </td>
                          <td className="py-3 px-4 font-sans font-bold">
                            <Link to={`/players/${player.player_id}`} className="text-[#F2F4F1] hover:text-[#FFC928] transition-colors">
                              {player.player_name}
                            </Link>
                          </td>
                          <td className="py-3 px-4 font-sans">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                              player.cohort === 'primary'
                                ? 'bg-white/10 text-[#F2F4F1]'
                                : 'bg-amber-500/15 text-amber-300'
                            }`}>
                              {player.cohort}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right text-[#F2F4F1]">
                            {player.balls_faced || player.legal_balls}
                          </td>
                          <td className="py-3 px-4 text-right text-[#A6A9A5]">
                            {player.match_count}
                          </td>
                          <td className="py-3 px-4 text-right font-bold text-[#FFC928]">
                            {player.strike_rate || player.economy_rate}
                          </td>
                          <td className="py-3 px-4 text-center">
                            <ClutchBadge score={player.clutch_iq} size="sm" showLabel={false} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {clusterDetail.players?.pagination && (
                  <div className="bg-[#25262A]/60 px-6 py-3.5 flex items-center justify-between border-t border-white/10 text-xs text-[#A6A9A5]">
                    <span>Page {page} of {clusterDetail.players.pagination.total_pages}</span>
                    <div className="flex items-center space-x-2">
                      <button
                        disabled={!clusterDetail.players.pagination.has_prev}
                        onClick={() => setPage(page - 1)}
                        className="px-3 py-1 rounded bg-white/5 disabled:opacity-30 border border-white/10 text-[#F2F4F1]"
                      >
                        Previous
                      </button>
                      <button
                        disabled={!clusterDetail.players.pagination.has_next}
                        onClick={() => setPage(page + 1)}
                        className="px-3 py-1 rounded bg-white/5 disabled:opacity-30 border border-white/10 text-[#F2F4F1]"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}

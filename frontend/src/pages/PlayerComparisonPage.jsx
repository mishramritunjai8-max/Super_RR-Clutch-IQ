import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  Scale, 
  Plus, 
  X, 
  Search, 
  Trophy, 
  ShieldCheck, 
  ArrowRight, 
  Info,
  BarChart3,
  Layers
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
import ClutchBadge from '../components/ClutchBadge';
import { TableSkeleton } from '../components/LoadingSkeleton';
import ErrorMessage from '../components/ErrorMessage';

export default function PlayerComparisonPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryIds = searchParams.get('player_ids');

  // Selected player IDs (default to 2533 and 7327 if not provided)
  const initialIds = queryIds
    ? queryIds.split(',').map((id) => parseInt(id.trim(), 10)).filter((id) => !isNaN(id))
    : [2533, 7327];

  const [selectedIds, setSelectedIds] = useState(initialIds);
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Search state for adding new players
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);

  const fetchComparison = async () => {
    if (selectedIds.length < 2) {
      setError('Please select at least 2 players to compare.');
      setComparisonData(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await api.comparePlayers(selectedIds);
      setComparisonData(res);
      setSearchParams({ player_ids: selectedIds.join(',') });
    } catch (err) {
      console.error('Failed to fetch player comparison:', err);
      setError(err.message || 'Error comparing selected players');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComparison();
  }, [selectedIds]);

  const handleAddPlayer = (playerId) => {
    if (selectedIds.includes(playerId)) return;
    if (selectedIds.length >= 5) {
      alert('You can compare a maximum of 5 players at a time.');
      return;
    }
    setSelectedIds([...selectedIds, playerId]);
    setSearchQuery('');
    setSearchResults([]);
  };

  const handleRemovePlayer = (playerId) => {
    if (selectedIds.length <= 2) {
      alert('A minimum of 2 players is required for comparison.');
      return;
    }
    setSelectedIds(selectedIds.filter((id) => id !== playerId));
  };

  const handleSearchPlayers = async (q) => {
    setSearchQuery(q);
    if (!q || q.length < 2) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    try {
      const res = await api.getBattersLeaderboard({ search: q, page: 1, page_size: 6, cohort: 'all' });
      setSearchResults(res.items || []);
    } catch {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  // Prepare chart data for Clutch IQ and Strike Rate / Economy
  const iqChartData = comparisonData?.players?.map((p) => ({
    name: p.player_name.split(' ').slice(-1)[0], // last name for chart brevity
    fullName: p.player_name,
    'Batting Clutch IQ': p.batting?.clutch_iq || 0,
    'Bowling Clutch IQ': p.bowling?.clutch_iq || 0,
  })) || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* 1. Header & Active Players Bar */}
      <div className="space-y-4 pb-6 border-b border-white/10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#FFC928]/15 border border-[#FFC928]/30 text-xs font-bold text-[#FFC928] mb-2 font-display">
              <Scale className="w-3.5 h-3.5" />
              <span>Side-by-Side Analytics</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-black font-display text-[#F2F4F1] uppercase">
              PLAYER COMPARISON
            </h1>
            <p className="text-xs sm:text-sm text-[#A6A9A5] mt-1">
              Objective pressure metrics, baseline elevation and archetype comparison for 2 to 5 players.
            </p>
          </div>

          {/* Add Player Search Box */}
          <div className="relative w-full sm:w-72">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearchPlayers(e.target.value)}
              placeholder="Add player by name..."
              disabled={selectedIds.length >= 5}
              className="w-full bg-[#25262A] border border-white/10 rounded-xl pl-9 pr-4 py-2 text-xs text-[#F2F4F1] placeholder-[#A6A9A5] focus:outline-none focus:border-[#FFC928] disabled:opacity-50"
            />
            <Search className="w-3.5 h-3.5 text-[#A6A9A5] absolute left-3 top-3" />

            {/* Autocomplete dropdown */}
            {searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 glass-panel-elevated rounded-xl p-2 z-30 shadow-2xl space-y-1 max-h-60 overflow-y-auto">
                {searchResults.map((result) => (
                  <button
                    key={result.player_id}
                    onClick={() => handleAddPlayer(result.player_id)}
                    className="w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-white/10 flex items-center justify-between text-[#F2F4F1] transition-colors"
                  >
                    <span>{result.player_name}</span>
                    <span className="text-[10px] text-[#FFC928] font-mono">#{result.player_id}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Selected Players Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-2">
          {comparisonData?.players?.map((p) => (
            <div
              key={p.player_id}
              className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs font-semibold text-[#F2F4F1]"
            >
              <span>{p.player_name}</span>
              <button
                onClick={() => handleRemovePlayer(p.player_id)}
                className="p-0.5 rounded-full hover:bg-white/10 text-[#A6A9A5] hover:text-rose-400 transition-colors"
                title="Remove player"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
          {selectedIds.length < 5 && (
            <span className="text-[11px] text-[#A6A9A5] italic">
              (You can compare up to {5 - selectedIds.length} more player{5 - selectedIds.length === 1 ? '' : 's'})
            </span>
          )}
        </div>
      </div>

      {loading ? (
        <TableSkeleton rows={8} />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchComparison} />
      ) : !comparisonData ? null : (
        <div className="space-y-10">
          {/* 2. Visual Comparison Chart */}
          <GlassCard className="p-6 space-y-4" hover={false}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-4 h-4 text-[#FFC928]" />
                <h3 className="text-sm uppercase tracking-wider font-bold text-[#F2F4F1] font-display">
                  Clutch IQ Comparison Chart
                </h3>
              </div>
              <span className="text-[11px] text-[#A6A9A5]">Bayesian Credibility Shrunk Scores [0–100]</span>
            </div>

            <div className="h-64 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={iqChartData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                  <XAxis dataKey="name" stroke="#A6A9A5" fontSize={12} tickLine={false} />
                  <YAxis stroke="#A6A9A5" fontSize={12} domain={[0, 100]} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1C1D20', borderColor: 'rgba(255,201,40,0.3)', borderRadius: '12px' }}
                    labelStyle={{ color: '#F2F4F1', fontWeight: 'bold' }}
                  />
                  <Legend wrapperStyle={{ paddingTop: '10px' }} />
                  <Bar dataKey="Batting Clutch IQ" fill="#FFC928" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="Bowling Clutch IQ" fill="#F2F4F1" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          {/* 3. Detailed Side-by-Side Metric Matrix Table */}
          <div className="glass-panel rounded-2xl overflow-hidden border border-white/10">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs sm:text-sm">
                <thead className="bg-[#25262A]/90 text-[#A6A9A5] uppercase text-[10px] tracking-wider border-b border-white/10 font-display">
                  <tr>
                    <th className="py-3.5 px-4 w-44">Metric / Dimension</th>
                    {comparisonData.players.map((p) => (
                      <th key={p.player_id} className="py-3.5 px-4 text-center">
                        <Link to={`/players/${p.player_id}`} className="hover:text-[#FFC928] transition-colors font-bold text-[#F2F4F1]">
                          {p.player_name}
                        </Link>
                        <span className="block text-[10px] text-[#A6A9A5] font-mono normal-case">
                          ID: {p.player_id}
                        </span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 font-mono text-xs">
                  {/* General Row: Archetypes */}
                  <tr className="bg-white/[0.02]">
                    <td className="py-3 px-4 font-sans font-bold text-[#F2F4F1] uppercase text-[11px]">Archetypes</td>
                    {comparisonData.players.map((p) => (
                      <td key={p.player_id} className="py-3 px-4 text-center font-sans text-[11px] text-[#A6A9A5]">
                        {p.batting && <div className="text-[#F2F4F1]"><span className="text-[#FFC928] font-bold">Bat:</span> {p.batting.archetype_name}</div>}
                        {p.bowling && <div className="text-[#F2F4F1] mt-0.5"><span className="text-[#FFC928] font-bold">Bowl:</span> {p.bowling.archetype_name}</div>}
                        {!p.batting && !p.bowling && '—'}
                      </td>
                    ))}
                  </tr>

                  {/* Section: BATTING METRICS */}
                  <tr className="bg-white/5 font-sans font-bold text-[#FFC928] text-xs">
                    <td colSpan={comparisonData.players.length + 1} className="py-2.5 px-4 uppercase tracking-wider">
                      Pressure Batting Performance
                    </td>
                  </tr>

                  <tr>
                    <td className="py-2.5 px-4 font-sans text-[#A6A9A5]">Batting Clutch IQ</td>
                    {comparisonData.players.map((p) => (
                      <td key={p.player_id} className="py-2.5 px-4 text-center font-bold text-[#FFC928]">
                        {p.batting?.clutch_iq ?? <span className="text-[#A6A9A5] font-normal">—</span>}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="py-2.5 px-4 font-sans text-[#A6A9A5]">Strike Rate (Pressure)</td>
                    {comparisonData.players.map((p) => (
                      <td key={p.player_id} className="py-2.5 px-4 text-center text-[#F2F4F1]">
                        {p.batting?.strike_rate ?? <span className="text-[#A6A9A5]">—</span>}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="py-2.5 px-4 font-sans text-[#A6A9A5]">Regularized Delta SR</td>
                    {comparisonData.players.map((p) => {
                      const delta = p.batting?.raw_delta_strike_rate;
                      return (
                        <td key={p.player_id} className={`py-2.5 px-4 text-center ${delta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {delta !== undefined ? (delta > 0 ? `+${delta}` : delta) : <span className="text-[#A6A9A5]">—</span>}
                        </td>
                      );
                    })}
                  </tr>

                  <tr>
                    <td className="py-2.5 px-4 font-sans text-[#A6A9A5]">Balls Faced / Matches</td>
                    {comparisonData.players.map((p) => (
                      <td key={p.player_id} className="py-2.5 px-4 text-center text-[#A6A9A5]">
                        {p.batting ? `${p.batting.balls_faced} balls (${p.batting.match_count} matches)` : '—'}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="py-2.5 px-4 font-sans text-[#A6A9A5]">Dot Ball % / Boundary %</td>
                    {comparisonData.players.map((p) => (
                      <td key={p.player_id} className="py-2.5 px-4 text-center text-[#A6A9A5]">
                        {p.batting ? `${p.batting.dot_ball_pct}% / ${p.batting.boundary_ball_pct}%` : '—'}
                      </td>
                    ))}
                  </tr>

                  {/* Section: BOWLING METRICS */}
                  <tr className="bg-white/5 font-sans font-bold text-[#FFC928] text-xs">
                    <td colSpan={comparisonData.players.length + 1} className="py-2.5 px-4 uppercase tracking-wider">
                      Pressure Bowling Performance
                    </td>
                  </tr>

                  <tr>
                    <td className="py-2.5 px-4 font-sans text-[#A6A9A5]">Bowling Clutch IQ</td>
                    {comparisonData.players.map((p) => (
                      <td key={p.player_id} className="py-2.5 px-4 text-center font-bold text-[#FFC928]">
                        {p.bowling?.clutch_iq ?? <span className="text-[#A6A9A5] font-normal">—</span>}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="py-2.5 px-4 font-sans text-[#A6A9A5]">Economy Rate (Pressure)</td>
                    {comparisonData.players.map((p) => (
                      <td key={p.player_id} className="py-2.5 px-4 text-center text-[#F2F4F1]">
                        {p.bowling?.economy_rate ?? <span className="text-[#A6A9A5]">—</span>}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="py-2.5 px-4 font-sans text-[#A6A9A5]">Raw Delta Economy</td>
                    {comparisonData.players.map((p) => {
                      const delta = p.bowling?.raw_delta_economy;
                      return (
                        <td key={p.player_id} className={`py-2.5 px-4 text-center ${delta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {delta !== undefined ? (delta > 0 ? `+${delta}` : delta) : <span className="text-[#A6A9A5]">—</span>}
                        </td>
                      );
                    })}
                  </tr>

                  <tr>
                    <td className="py-2.5 px-4 font-sans text-[#A6A9A5]">Legal Balls / Wickets</td>
                    {comparisonData.players.map((p) => (
                      <td key={p.player_id} className="py-2.5 px-4 text-center text-[#A6A9A5]">
                        {p.bowling ? `${p.bowling.legal_balls} balls / ${p.bowling.bowler_wickets} wkts` : '—'}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="py-2.5 px-4 font-sans text-[#A6A9A5]">Bowling Strike Rate</td>
                    {comparisonData.players.map((p) => (
                      <td key={p.player_id} className="py-2.5 px-4 text-center text-[#A6A9A5]">
                        {p.bowling?.bowling_strike_rate ? `${p.bowling.bowling_strike_rate} balls/wkt` : '—'}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

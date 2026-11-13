/**
 * SUPER RR — CLUTCH IQ
 * Centralized API Client Service
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function fetchJson(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!res.ok) {
      let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
      try {
        const errorData = await res.json();
        if (errorData && errorData.detail) {
          errorDetail = errorData.detail;
        }
      } catch {
        // Fallback to status text
      }
      const error = new Error(errorDetail);
      error.status = res.status;
      throw error;
    }

    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // System & Metadata
  getHealth: () => fetchJson('/health'),
  getMetadata: () => fetchJson('/metadata'),

  // Leaderboards
  getBattersLeaderboard: (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.set('page', params.page);
    if (params.page_size) searchParams.set('page_size', params.page_size);
    if (params.cohort) searchParams.set('cohort', params.cohort);
    if (params.sort_by) searchParams.set('sort_by', params.sort_by);
    if (params.sort_order) searchParams.set('sort_order', params.sort_order);
    if (params.search) searchParams.set('search', params.search);
    if (params.min_balls) searchParams.set('min_balls', params.min_balls);
    if (params.min_matches) searchParams.set('min_matches', params.min_matches);
    const qs = searchParams.toString();
    return fetchJson(`/leaderboards/batters${qs ? `?${qs}` : ''}`);
  },

  getBowlersLeaderboard: (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.set('page', params.page);
    if (params.page_size) searchParams.set('page_size', params.page_size);
    if (params.cohort) searchParams.set('cohort', params.cohort);
    if (params.sort_by) searchParams.set('sort_by', params.sort_by);
    if (params.sort_order) searchParams.set('sort_order', params.sort_order);
    if (params.search) searchParams.set('search', params.search);
    if (params.min_balls) searchParams.set('min_balls', params.min_balls);
    if (params.min_matches) searchParams.set('min_matches', params.min_matches);
    const qs = searchParams.toString();
    return fetchJson(`/leaderboards/bowlers${qs ? `?${qs}` : ''}`);
  },

  // Players
  getPlayerSummary: (playerId) => fetchJson(`/players/${playerId}`),
  getPlayerBattingProfile: (playerId) => fetchJson(`/players/${playerId}/batting`),
  getPlayerBowlingProfile: (playerId) => fetchJson(`/players/${playerId}/bowling`),
  
  comparePlayers: (playerIds = []) => {
    const ids = Array.isArray(playerIds) ? playerIds.join(',') : playerIds;
    return fetchJson(`/players/compare?player_ids=${encodeURIComponent(ids)}`);
  },

  // Archetypes
  getBattingArchetypes: () => fetchJson('/archetypes/batting'),
  getBattingArchetypeDetail: (clusterId, params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.set('page', params.page);
    if (params.page_size) searchParams.set('page_size', params.page_size);
    const qs = searchParams.toString();
    return fetchJson(`/archetypes/batting/${clusterId}${qs ? `?${qs}` : ''}`);
  },

  getBowlingArchetypes: () => fetchJson('/archetypes/bowling'),
  getBowlingArchetypeDetail: (clusterId, params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.set('page', params.page);
    if (params.page_size) searchParams.set('page_size', params.page_size);
    const qs = searchParams.toString();
    return fetchJson(`/archetypes/bowling/${clusterId}${qs ? `?${qs}` : ''}`);
  },

  // Macro Analytics & Pressure Segments
  getAnalyticsSummary: () => fetchJson('/analytics/summary'),
  getPressureAnalytics: () => fetchJson('/analytics/pressure'),
};

export default api;

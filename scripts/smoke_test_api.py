"""
Smoke test script for FastAPI endpoints
"""

import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from backend.api.main import app

def main():
    print("Initializing TestClient...")
    with TestClient(app) as client:
        # 1. Health
        t0 = time.perf_counter()
        res = client.get("/api/v1/health")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Health failed: {res.text}"
        data = res.json()
        print(f"GET /api/v1/health -> 200 OK ({(t1-t0)*1000:.1f}ms): status={data['status']}")
        
        # 2. Metadata
        t0 = time.perf_counter()
        res = client.get("/api/v1/metadata")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Metadata failed: {res.text}"
        data = res.json()
        print(f"GET /api/v1/metadata -> 200 OK ({(t1-t0)*1000:.1f}ms): reg_players={data['total_registered_players']}")
        
        # 3. Batters leaderboard
        t0 = time.perf_counter()
        res = client.get("/api/v1/leaderboards/batters?limit=5&cohort=primary")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Batters leaderboard failed: {res.text}"
        data = res.json()
        print(f"GET /api/v1/leaderboards/batters -> 200 OK ({(t1-t0)*1000:.1f}ms): items={len(data['items'])}, total={data['pagination']['total_records']}")
        top_batter = data['items'][0]
        print(f"   Top Batter: #{top_batter['rank']} {top_batter['player_name']} (IQ={top_batter['clutch_iq']}, Archetype={top_batter['archetype_name']})")
        
        # 4. Bowlers leaderboard
        t0 = time.perf_counter()
        res = client.get("/api/v1/leaderboards/bowlers?limit=5&cohort=primary")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Bowlers leaderboard failed: {res.text}"
        data = res.json()
        print(f"GET /api/v1/leaderboards/bowlers -> 200 OK ({(t1-t0)*1000:.1f}ms): items={len(data['items'])}, total={data['pagination']['total_records']}")
        top_bowler = data['items'][0]
        print(f"   Top Bowler: #{top_bowler['rank']} {top_bowler['player_name']} (IQ={top_bowler['clutch_iq']}, Archetype={top_bowler['archetype_name']})")
        
        # 5. Player detail
        player_id = top_batter['player_id']
        t0 = time.perf_counter()
        res = client.get(f"/api/v1/players/{player_id}")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Player detail failed: {res.text}"
        pdata = res.json()
        print(f"GET /api/v1/players/{player_id} -> 200 OK ({(t1-t0)*1000:.1f}ms): name={pdata['player_name']}, has_batting={pdata['has_batting_profile']}, has_bowling={pdata['has_bowling_profile']}")
        
        # 6. Player batting profile
        t0 = time.perf_counter()
        res = client.get(f"/api/v1/players/{player_id}/batting")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Player batting failed: {res.text}"
        print(f"GET /api/v1/players/{player_id}/batting -> 200 OK ({(t1-t0)*1000:.1f}ms)")
        
        # 7. Player comparison
        bowler_id = top_bowler['player_id']
        t0 = time.perf_counter()
        res = client.get(f"/api/v1/players/compare?player_ids={player_id},{bowler_id}")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Player compare failed: {res.text}"
        cdata = res.json()
        print(f"GET /api/v1/players/compare -> 200 OK ({(t1-t0)*1000:.1f}ms): returned {len(cdata['players'])} players")
        
        # 8. Batting Archetypes
        t0 = time.perf_counter()
        res = client.get("/api/v1/archetypes/batting")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Archetypes batting failed: {res.text}"
        print(f"GET /api/v1/archetypes/batting -> 200 OK ({(t1-t0)*1000:.1f}ms): {len(res.json())} archetypes")
        
        # 9. Batting Archetype Detail
        t0 = time.perf_counter()
        res = client.get("/api/v1/archetypes/batting/0")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Archetype 0 failed: {res.text}"
        print(f"GET /api/v1/archetypes/batting/0 -> 200 OK ({(t1-t0)*1000:.1f}ms): {res.json()['profile']['archetype_name']}, players={len(res.json()['players']['items'])}")
        
        # 10. Analytics Summary
        t0 = time.perf_counter()
        res = client.get("/api/v1/analytics/summary")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Analytics summary failed: {res.text}"
        adata = res.json()
        print(f"GET /api/v1/analytics/summary -> 200 OK ({(t1-t0)*1000:.1f}ms): total_deliv={adata['total_deliveries']}, reg={adata['regular_innings_deliveries']}, super_over={adata['super_over_deliveries']}")
        
        # 11. Pressure Analytics
        t0 = time.perf_counter()
        res = client.get("/api/v1/analytics/pressure")
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Pressure analytics failed: {res.text}"
        pdata = res.json()
        print(f"GET /api/v1/analytics/pressure -> 200 OK ({(t1-t0)*1000:.1f}ms): {len(pdata['segments'])} segments")
        
    print("\nALL SMOKE CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()

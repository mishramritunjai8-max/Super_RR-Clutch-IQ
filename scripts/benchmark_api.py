"""
SUPER RR — CLUTCH IQ
FastAPI Latency Benchmark & Performance Audit
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import statistics
from fastapi.testclient import TestClient
from backend.api.main import app

def benchmark_endpoint(client, endpoint: str, name: str, iterations: int = 20):
    latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        res = client.get(endpoint)
        t1 = time.perf_counter()
        assert res.status_code == 200, f"Benchmark failed for {endpoint}: {res.text}"
        latencies.append((t1 - t0) * 1000.0)
        
    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
    mean_lat = statistics.mean(latencies)
    min_lat = min(latencies)
    max_lat = max(latencies)
    
    return {
        "endpoint": endpoint,
        "name": name,
        "mean_ms": round(mean_lat, 2),
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "min_ms": round(min_lat, 2),
        "max_ms": round(max_lat, 2)
    }

def main():
    print("=" * 80)
    print("SUPER RR — CLUTCH IQ: FASTAPI BACKEND PERFORMANCE BENCHMARK")
    print("=" * 80)
    
    endpoints = [
        ("/health", "Top-Level Health Check"),
        ("/api/v1/health", "API v1 Health Check"),
        ("/api/v1/metadata", "System & Dataset Metadata"),
        ("/api/v1/leaderboards/batters?page=1&page_size=20", "Batting Leaderboard (Default Page)"),
        ("/api/v1/leaderboards/batters?cohort=all&page_size=50", "Batting Leaderboard (All Cohorts, 50 Items)"),
        ("/api/v1/leaderboards/bowlers?page=1&page_size=20", "Bowling Leaderboard (Default Page)"),
        ("/api/v1/leaderboards/bowlers?cohort=all&page_size=50", "Bowling Leaderboard (All Cohorts, 50 Items)"),
        ("/api/v1/players/23", "Player Profile (All-Rounder: Piyush Chawla)"),
        ("/api/v1/players/2533", "Player Profile (Bat-Only: Najibullah Zadran)"),
        ("/api/v1/players/7327", "Player Profile (Bowl-Only: Rasikh Salam)"),
        ("/api/v1/players/2533/batting", "Player Batting Profile (Najibullah Zadran)"),
        ("/api/v1/players/7327/bowling", "Player Bowling Profile (Rasikh Salam)"),
        ("/api/v1/players/compare?player_ids=2533,7327,23,47,8", "Player Comparison (5 Players)"),
        ("/api/v1/archetypes/batting", "Batting Archetypes List"),
        ("/api/v1/archetypes/batting/0?page_size=20", "Batting Archetype Detail (Cluster 0)"),
        ("/api/v1/archetypes/bowling", "Bowling Archetypes List"),
        ("/api/v1/archetypes/bowling/1?page_size=20", "Bowling Archetype Detail (Cluster 1)"),
        ("/api/v1/analytics/summary", "Macro Dataset Summary"),
        ("/api/v1/analytics/pressure", "Pressure Segment Analytics (8 Segments)")
    ]
    
    results = []
    with TestClient(app) as client:
        # Warm-up request
        client.get("/api/v1/health")
        
        for ep, label in endpoints:
            res = benchmark_endpoint(client, ep, label, iterations=25)
            results.append(res)
            print(f"[{res['p50_ms']:5.1f}ms p50 | {res['p95_ms']:5.1f}ms p95]  {res['name']} ({res['endpoint']})")
            
    print("=" * 80)
    print("BENCHMARK SUMMARY TABLE:")
    print(f"{'Endpoint Name':<42} | {'Mean (ms)':<9} | {'p50 (ms)':<8} | {'p95 (ms)':<8} | {'Min/Max (ms)'}")
    print("-" * 80)
    for r in results:
        min_max = f"{r['min_ms']:.1f}/{r['max_ms']:.1f}"
        print(f"{r['name']:<42} | {r['mean_ms']:<9.1f} | {r['p50_ms']:<8.1f} | {r['p95_ms']:<8.1f} | {min_max}")
    print("=" * 80)

if __name__ == "__main__":
    main()

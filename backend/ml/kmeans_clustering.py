"""
SUPER RR — CLUTCH IQ
Phase 4: K-Means Clustering & Model Training Engine (Corrected)

Implements:
1. Systematic candidate K evaluation across multiple validation criteria
   (Silhouette Score, Davies-Bouldin Index, Calinski-Harabasz Index, Inertia,
    min/max cluster sizes, and cluster balance ratio).
2. Seed stability analysis across multiple random seeds via Adjusted Rand Index (ARI).
3. Deterministic training of K-Means models on primary eligible cohorts.
4. Complete serialization of models, scalers, and transparent metadata.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    adjusted_rand_score
)
from typing import Dict, List, Tuple, Optional


# Set thread count environment variable to avoid Windows wmic loky warnings
os.environ["LOKY_MAX_CPU_COUNT"] = "4"


def evaluate_k_candidates(
    X_scaled: np.ndarray,
    k_range: range = range(2, 9),
    random_state: int = 42,
    n_init: int = 20
) -> pd.DataFrame:
    """
    Evaluates candidate cluster counts K in [k_min, k_max] across five
    complementary statistical validation metrics and cluster size balance.
    """
    records = []
    
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=random_state, n_init=n_init, max_iter=300)
        labels = km.fit_predict(X_scaled)
        
        sil = float(silhouette_score(X_scaled, labels))
        db = float(davies_bouldin_score(X_scaled, labels))
        ch = float(calinski_harabasz_score(X_scaled, labels))
        inertia = float(km.inertia_)
        
        counts = pd.Series(labels).value_counts().sort_index().to_dict()
        min_size = int(min(counts.values()))
        max_size = int(max(counts.values()))
        balance_ratio = round(min_size / max_size, 4)
        
        records.append({
            "k": k,
            "silhouette_score": round(sil, 4),
            "davies_bouldin_index": round(db, 4),
            "calinski_harabasz_index": round(ch, 2),
            "inertia": round(inertia, 2),
            "min_cluster_size": min_size,
            "max_cluster_size": max_size,
            "balance_ratio": balance_ratio,
            "cluster_sizes": str(counts)
        })
        
    return pd.DataFrame(records)


def evaluate_seed_stability(
    X_scaled: np.ndarray,
    k: int,
    seeds: Optional[List[int]] = None,
    n_init: int = 20
) -> Dict[str, float]:
    """
    Evaluates clustering partition stability across multiple random seeds
    using Adjusted Rand Index (ARI) compared to the base seed (42).
    """
    if seeds is None:
        seeds = [42, 100, 2024, 7, 999]
        
    base_km = KMeans(n_clusters=k, random_state=seeds[0], n_init=n_init, max_iter=300)
    base_labels = base_km.fit_predict(X_scaled)
    
    stability_scores = {}
    for seed in seeds[1:]:
        km = KMeans(n_clusters=k, random_state=seed, n_init=n_init, max_iter=300)
        labels = km.fit_predict(X_scaled)
        ari = float(adjusted_rand_score(base_labels, labels))
        stability_scores[f"seed_{seed}_vs_base"] = round(ari, 4)
        
    stability_scores["mean_ari"] = round(float(np.mean(list(stability_scores.values()))), 4)
    return stability_scores


def train_kmeans_model(
    X_scaled: np.ndarray,
    k: int,
    random_state: int = 42,
    n_init: int = 20
) -> KMeans:
    """
    Trains a deterministic K-Means model on the primary scaled feature matrix.
    """
    km = KMeans(n_clusters=k, random_state=random_state, n_init=n_init, max_iter=300)
    km.fit(X_scaled)
    return km


def save_phase4_model_artifacts(
    role: str,
    model: KMeans,
    scaler: object,
    features: List[str],
    k: int,
    validation_df: pd.DataFrame,
    seed_stability: Dict[str, float],
    imputation_stats: Dict,
    excluded_features: Dict[str, str],
    output_dir: str = "models/phase4"
) -> Dict[str, str]:
    """
    Serializes trained K-Means models, scalers, and configuration metadata.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, f"{role}_kmeans_model.joblib")
    scaler_path = os.path.join(output_dir, f"{role}_scaler.joblib")
    meta_path = os.path.join(output_dir, f"{role}_metadata.json")
    
    # 1. Save model and scaler via joblib
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    # 2. Extract cluster sizes and inertia
    labels = model.labels_
    cluster_counts = {int(k_id): int(c) for k_id, c in pd.Series(labels).value_counts().sort_index().items()}
    
    # Scaler parameters
    scaler_means = [round(float(m), 4) for m in getattr(scaler, "mean_", [])]
    scaler_scales = [round(float(s), 4) for s in getattr(scaler, "scale_", [])]
    
    metadata = {
        "role": role,
        "engine_version": "4.1.0",
        "selected_k": k,
        "random_state": 42,
        "n_init": 20,
        "max_iter": 300,
        "features": features,
        "num_features": len(features),
        "primary_sample_size": len(labels),
        "cluster_sizes": cluster_counts,
        "cluster_balance_ratio": round(min(cluster_counts.values()) / max(cluster_counts.values()), 4),
        "inertia": round(float(model.inertia_), 2),
        "scaling": {
            "type": type(scaler).__name__,
            "means": dict(zip(features, scaler_means)),
            "scales": dict(zip(features, scaler_scales))
        },
        "imputation_statistics": imputation_stats,
        "excluded_redundant_features": excluded_features,
        "seed_stability": seed_stability,
        "candidate_validation_summary": validation_df.to_dict(orient="records")
    }
    
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
    return {
        "model_path": model_path,
        "scaler_path": scaler_path,
        "meta_path": meta_path
    }

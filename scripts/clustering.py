import pandas as pd
import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt
import os

os.makedirs("imgs", exist_ok=True)

df_micro = pd.read_csv("data/moods_microacts.csv")

non_behavioral = [
    "sunny", "clouds", "rain", "storm", "wind", "heat", "humid", "cold",
    "happy", "excited", "grateful", "relaxed", "content", "tired", "unsure",
    "bored", "anxious", "angry", "stressed", "sad", "desperate", "irritated"
]
df_micro_clustering = df_micro.drop(columns=[c for c in non_behavioral if c in df_micro.columns])

# Activity frequency check — before clustering, so you know what you're feeding it
activity_freq = df_micro_clustering.mean().sort_values(ascending=False)
print(activity_freq.head(10))
print(activity_freq.tail(10))

X = df_micro_clustering.values
jaccard_dist_matrix = pairwise_distances(X, metric='jaccard')
Z = linkage(X, method="average", metric="jaccard")

plt.figure(figsize=(12, 6))
dendrogram(Z, no_labels=True, color_threshold=None)
plt.title("Hierarchical Clustering Dendrogram (Jaccard Distance)")
plt.xlabel("Mood entries"); plt.ylabel("Distance")
plt.tight_layout()
plt.savefig("imgs/dendrogram_full.png", dpi=150)
plt.show()

plt.figure(figsize=(12, 6))
dendrogram(Z, truncate_mode="lastp", p=30, show_leaf_counts=True)
plt.title("Truncated Dendrogram (Top 30 Clusters)")
plt.ylabel("Distance")
plt.tight_layout()
plt.savefig("imgs/dendrogram_truncated.png", dpi=150)
plt.show()

# Gap analysis — run BEFORE picking any cut height
merge_heights = Z[:, 2]
gaps = np.diff(merge_heights)
top_gap_idx = np.argsort(gaps)[::-1][:10]
for i in sorted(top_gap_idx):
    print(f"Gap of {gaps[i]:.4f} between merge distance {merge_heights[i]:.4f} and {merge_heights[i+1]:.4f}")

# Pick cuts based on gap analysis output
# Three resolutions, each anchored to one of the current top gaps:
# fine:   inside 0.7885–0.8335 (3rd-largest gap)
# main:   inside 0.8758–0.9323 (2nd-largest gap)
# coarse: inside 0.9413–1.0000 (largest gap)

clusters_fine = fcluster(Z, t=0.81, criterion="distance")
clusters_main = fcluster(Z, t=0.90, criterion="distance")
clusters_coarse = fcluster(Z, t=0.95, criterion="distance")

df_clusters = df_micro.copy()
df_clusters["cluster_fine"] = clusters_fine
df_clusters["cluster_main"] = clusters_main
df_clusters["cluster_coarse"] = clusters_coarse

print(df_clusters["cluster_fine"].value_counts())
print(df_clusters["cluster_main"].value_counts())
print(df_clusters["cluster_coarse"].value_counts())

# Examine relevant (main) clusters and identify top activities in each

activity_cols = [c for c in df_micro.columns if c not in ["cluster_fine", "cluster_main", "cluster_coarse"]]

for tier in ["cluster_fine", "cluster_main", "cluster_coarse"]:
    print(f"\n########## {tier} ##########")
    for label in sorted(df_clusters[tier].unique()):
        subset = df_clusters[df_clusters[tier] == label]
        n = len(subset)
        print(f"\n=== {tier} {label} (n={n}) ===")
        print(subset[activity_cols].sum().sort_values(ascending=False).head(10))

print(df_clusters[df_clusters["cluster_main"] == df_clusters["cluster_main"].value_counts().idxmin()])

# Bring back dates to inspect outlier cluster against period of time.
df_dates = pd.read_csv("data/moods_cleaned.csv")

# Confirm row counts match between relevant dfs
print(len(df_dates), len(df_micro))

# Check dates

for tier in ["cluster_fine", "cluster_main", "cluster_coarse"]:
    print(f"\n########## {tier} dates ##########")
    for label in sorted(df_clusters[tier].unique()):
        idx = df_clusters[df_clusters[tier] == label].index
        print(f"\n=== {tier} {label} dates (n={len(idx)}) ===")
        print(df_dates.loc[idx, "full_date"])

#Create clusters file to feed into the dashboard clusters section
cluster_export = df_clusters[["cluster_fine", "cluster_main", "cluster_coarse"]].copy()
cluster_export["full_date"] = df_dates.loc[cluster_export.index, "full_date"].values
cluster_export.to_csv("data/cluster_assignments.csv", index=False)
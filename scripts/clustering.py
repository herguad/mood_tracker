import pandas as pd
import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt

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
plt.tight_layout(); plt.show()

plt.figure(figsize=(12, 6))
dendrogram(Z, truncate_mode="lastp", p=30, show_leaf_counts=True)
plt.title("Truncated Dendrogram (Top 30 Clusters)")
plt.ylabel("Distance")
plt.tight_layout(); plt.show()

# Gap analysis — run BEFORE picking any cut height
merge_heights = Z[:, 2]
gaps = np.diff(merge_heights)
top_gap_idx = np.argsort(gaps)[::-1][:10]
for i in sorted(top_gap_idx):
    print(f"Gap of {gaps[i]:.4f} between merge distance {merge_heights[i]:.4f} and {merge_heights[i+1]:.4f}")

# Pick cuts based on gap analysis output
# Main clustering: narrow behavioural modes
# Coarse clustering: broad behavioural modes

clusters_main = fcluster(Z, t=0.85, criterion="distance")
clusters_coarse = fcluster(Z, t=0.95, criterion="distance")

#Attach clusters back to the data

df_clusters = df_micro.copy()
df_clusters["cluster_main"] = clusters_main
df_clusters["cluster_coarse"] = clusters_coarse

#Cluster sizes
print(df_clusters["cluster_main"].value_counts()) 
print(df_clusters["cluster_coarse"].value_counts()) 

# Examine relevant (main) clusters and identify top activities in each

activity_cols = [c for c in df_micro.columns if c not in ["cluster_main", "cluster_coarse"]]

for label in sorted(df_clusters["cluster_main"].unique()):
    subset = df_clusters[df_clusters["cluster_main"] == label]
    n = len(subset)
    print(f"\n=== cluster_main {label} (n={n}) ===")
    print(subset[activity_cols].sum().sort_values(ascending=False).head(10))

print(df_clusters[df_clusters["cluster_main"] == df_clusters["cluster_main"].value_counts().idxmin()])

# Bring back dates to inspect outlier cluster against period of time.
df_dates = pd.read_csv("data/moods_cleaned.csv")

# Confirm row counts match between relevant dfs
print(len(df_dates), len(df_micro))

# Check dates
cluster3_idx = df_clusters[df_clusters["cluster_main"] == 3].index
print(df_dates.loc[cluster3_idx, "full_date"])

for cluster_label in [2, 4]:
    idx = df_clusters[df_clusters["cluster_main"] == cluster_label].index
    print(f"\n=== cluster_main {cluster_label} dates ===")
    print(df_dates.loc[idx, "full_date"])


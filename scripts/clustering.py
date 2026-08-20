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
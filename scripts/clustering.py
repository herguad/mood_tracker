import pandas as pd
import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram
from scipy.cluster.hierarchy import fcluster
import matplotlib.pyplot as plt
#from sklearn.decomposition import PCA
#from sklearn.cluster import KMeans
#from sklearn.preprocessing import StandardScaler

#Load microactivities 

df_micro = pd.read_csv("data\moods_microacts.csv")

print(df_micro.head())
print(df_micro.info())

#compute Jaccard distance between entries --> see Jaccard index in binary classification confusion matrices

X = df_micro.values

## D[i, j] will be the distance between X[i] and Y[j]
jaccard_dist_matrix = pairwise_distances(X, metric='jaccard')

#Check matrix
print(jaccard_dist_matrix.shape)
print(jaccard_dist_matrix.min(), jaccard_dist_matrix.max())


#perform linkage

Z = linkage(X, method="average", metric="jaccard")

#inspect dendrogram

plt.figure(figsize=(12, 6))
dendrogram(Z,no_labels=True,color_threshold=None)

plt.title("Hierarchical Clustering Dendrogram (Jaccard Distance)")
plt.xlabel("Mood entries")
plt.ylabel("Distance")

plt.tight_layout()
plt.show()

#Plot truncated for more precision
plt.figure(figsize=(12, 6))
dendrogram(
    Z,
    truncate_mode="lastp",
    p=30,
    show_leaf_counts=True
)

plt.title("Truncated Dendrogram (Top 30 Clusters)")
plt.ylabel("Distance")

plt.tight_layout()
plt.show()

### At distance X, Y number of clusters remaining if we cut at X
# 0.8 < X < 0.93, Y = 5-7
# 0.8 < X < 0.85, Y = 8-10
# 0.9 < X < 1, Y = 4

# Activity patterns 

clusters_main = fcluster(Z, t=0.88, criterion="distance")

#Coarse clustering: broad behavioural modes

clusters_coarse = fcluster(Z, t=0.93, criterion="distance")

#Attach clusters back to the data

df_clusters = df_micro.copy()
df_clusters["cluster_main"] = clusters_main
df_clusters["cluster_coarse"] = clusters_coarse

#Cluster sizes
print(df_clusters["cluster_main"].value_counts()) 
print(df_clusters["cluster_coarse"].value_counts()) 

########Label rare activity profiles

cluster_counts = pd.Series(clusters_main).value_counts()
rare_clusters = cluster_counts[cluster_counts < 5].index

#Inspect rare rows

df_clusters["cluster_main_clean"] = df_clusters["cluster_main"]
df_clusters.loc[
    df_clusters["cluster_main"].isin(rare_clusters),
    "cluster_main_clean"
] = -1


#Re-cluster excluding rare profiles
mask_core = ~df_clusters["cluster_main"].isin(rare_clusters)

X_core = X[mask_core]

Z_core = linkage(X_core, method="average", metric="jaccard")

#Replot and re-inspect dendrogram

plt.figure(figsize=(12, 6))
dendrogram(Z_core,no_labels=True,color_threshold=None)

plt.title("Hierarchical Clustering Dendrogram (Jaccard Distance)")
plt.xlabel("Mood entries")
plt.ylabel("Distance")

plt.tight_layout()
plt.show()

#Plot truncated for more precision
plt.figure(figsize=(12, 6))
dendrogram(
    Z_core,
    truncate_mode="lastp",
    p=30,
    show_leaf_counts=True
)

plt.title("Truncated Dendrogram (Top 30 Clusters)")
plt.ylabel("Distance")

plt.tight_layout()
plt.show()


#Re-cut clusters

# Activity patterns 

clusters_main = fcluster(Z_core, t=0.75, criterion="distance")

#Coarse clustering: broad behavioural modes

clusters_coarse = fcluster(Z_core, t=0.82, criterion="distance")

# Check no clusters are <10 observations and no cluster
# Check no cluster dominates > 45%50% 
validate_s= pd.Series(clusters_main).value_counts().sort_values(ascending=False)
print(validate_s)

#Attach clusters back to the data

df_clusters = df_micro.loc[mask_core].copy()

df_clusters["cluster_main"] = clusters_main
df_clusters["cluster_coarse"] = clusters_coarse

#print(type(df_clusters["cluster_main"]))

print(df_clusters["cluster_main"].value_counts())


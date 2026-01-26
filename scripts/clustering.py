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

Z = linkage(jaccard_dist_matrix,method="average")

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

### 5 gaps at > 4.0 distance 9/10 gaps at 3.5.

#Fine-grained clustering: activity patterns


#Coarse clustering:broad behavioural modes




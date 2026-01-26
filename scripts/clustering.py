import pandas as pd
import numpy as np
from sklearn.metrics import pairwise_distances
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
#from scipy.cluster.hierarchy import linkage

#Z = linkage(jaccard_dist_matrix,method="average")


#inspect dendrogram
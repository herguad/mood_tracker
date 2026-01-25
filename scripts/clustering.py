import pandas as pd
import numpy as np

#Load microactivities 

df_micro = pd.read_csv("data\moods_microacts.csv")

print(df_micro.head())
print(df_micro.describe())

#compute Jaccard distance between entries

#perform linkage

#inspect dendrogram
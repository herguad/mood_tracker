# Initial EDA and cleaning

## General structure

- cleaning.py → produces moods_cleaned.csv

- load_db.py → loads facts into SQLite

- features.ipynb / analysis.R → built features & models

Raw data is cleaned in Python, stored normalized in SQL, and enriched analytically downstream.

'Activities' are derived features generated in the analysis pipeline and therefore not stored in the database.

The dataset does not include a continuous or ordinal measure of mood intensity.
As a result, the analysis focuses on categorical mood patterns, temporal dynamics, and activity context rather than affect strength.

Exploratory plots were implemented using Matplotlib for structural time-based visualizations and Seaborn for categorical and distributional analyses

## Temporal structure (always first)

- Questions:

1. How long is the tracking period?

2. Are there gaps?

3. Is frequency stable?

- Plots:

1. Entries per week/month

2. Rolling counts

## Mood distribution

- Questions:

1. Are moods balanced?

2. Are some moods rare?

- Plots:

1. Mood counts

## Activity structure
- Questions:

1. Which activities dominate?

2. How sparse is the matrix?

3. Are some activities redundant?

- Plots:

1. Column sums

2. Heatmap of correlations

3. Co-occurrence counts


## Mood × Activity interaction

- Questions:

1. Which activities co-occur with which moods?

2. Are some moods activity-driven?

3. Is there separation potential for clustering?

- Plots:

1. Heatmap (mood vs activity)
“---- is relatively more common when mood = X”

“------ share similar activity profiles”

“------------ do not differentiate moods”

Motivates:

clustering

dimensionality reduction

grouping decisions

2. Conditional probabilities

clustering mood entries based on their activity profiles
each row is: one mood entry represented as a binary vector of activities
Mood labels were excluded from the clustering input and used only post hoc to interpret cluster composition.

Because data (df_micro) is binary and sparse, better choices for distance measurement are: cosine8(pattern similarity) , Jaccard (presence/absence similarity) or Hamming (exact mismatches count).

Pairwise Jaccard distances were computed between mood entries based on binary activity profiles, capturing similarity in activity context.

Hierarchical clustering was performed using average linkage with Jaccard distance computed directly within the linkage procedure, ensuring correct handling of binary multi-label activity data.

Observations 

At distance X, Y number of clusters remaining if we cut at X

- 0.8 < X < 0.93, Y = 5-7
most stable region. Merges slow down
Clusters are internally coherent, externally distinct

- 0.8 < X < 0.85, Y = 8-10
Fine-grained behavioral contexts
Many clusters are still relatively cohesive
This cut yields many clusters, but some are already merging fast

- 0.9 < X < 1, Y = 4
3–4 macro clusters
High-level lifestyle modes
### ----------------------------------------------------
- Python (notebook) → EDA + plots

- R → optional deeper stats or contrasts

- SQL → sanity checks, time-based aggregates
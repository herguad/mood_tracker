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

1. *Entries per week/month*

2. **Rolling counts**

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

2. Conditional probabilities

### ----------------------------------------------------
- Python (notebook) → EDA + plots

- R → optional deeper stats or contrasts

- SQL → sanity checks, time-based aggregates
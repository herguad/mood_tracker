# Initial EDA and cleaning

## General structure

- cleaning.py → produces moods_cleaned.csv

- load_db.py → loads facts into SQLite

- features.ipynb / analysis.R → built features & models

Raw data is cleaned in Python, stored normalized in SQL, and enriched analytically downstream.

'Activities' are derived features generated in the analysis pipeline and therefore not stored in the database.

The dataset does not include a continuous or ordinal measure of mood intensity.
As a result, the analysis focuses on categorical mood patterns, temporal dynamics, and activity context rather than affect strength.

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


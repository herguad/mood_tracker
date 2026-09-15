# Mood Tracker 

A personal daily mood-tracking dataset (Daylio export), analyzed to demonstrate data cleaning, EDA, and unsupervised ML skills across Python, SQL, and R.

## Pipeline overview

```
data/raw_mood.csv
      │
      ▼
scripts/cleaning.py  ──────►  data/moods_cleaned.csv
      │                       data/moods_microacts.csv   (binary micro-activity matrix)
      │                       data/moods_features.csv    (micro + macro binary columns)
      ▼
scripts/load_db.py  ───────►  data/moods.db (SQLite)
      │
      ▼
notebooks/EDA_mood_t.ipynb  ─►  EDA plots, hierarchical clustering
scripts/clustering.py       ─►  standalone clustering script (mirrors notebook)
scripts/analysis.R          ─►  optional deeper stats / contrasts
```

`load_db.py` fully replaces the `moods` table on each run (`if_exists="replace"`), so it always mirrors the current `moods_cleaned.csv` rather than accumulating duplicate rows across re-runs.

Activities are derived, multi-label features generated during cleaning (not stored in the raw database).

The dataset has no continuous or ordinal mood-intensity measure, so analysis focuses on categorical mood patterns, temporal dynamics, and activity context rather than affect strength.

## Activity categories: micro vs. macro

Each logged activity is captured at two levels of granularity:

- **Micro** : the individual activity tags as logged (e.g. `gardening`, `call_mom`, `medium sleep`).
- **Macro** : 8 broader categories each micro-activity is mapped into: `emotions`, `sleep`, `health`, `social`, `better_me`, `productivity`, `chores`, `weather`.

Macro categories exist for **narrative and interpretability**, not for clustering — they're used to summarize and explain findings (e.g. "this cluster skews toward health + social") rather than as the feature space for the unsupervised model itself, where the finer-grained micro-activities are used instead.

Two infrequently-logged tag groups were folded into an existing macro category rather than kept as sparse standalone signals:
- Food-related tags (`eat healthy`, `fast food`, `restaurant`, `homemade`, `no meat`, `delivery`) → folded into `health`.
- `craft` (logged only briefly, in January) → folded into `better_me`.

Both are noted here rather than treated as meaningful findings on their own, given how little signal they carry.

## Temporal segmentation

A `period` column splits entries into `pre` / `post` around a fixed cutoff (2026-02-01), marking a personal loss experienced in early 2026. This is treated as an objective structural break in the time series, analyzed as a separate cohort (not blended into a single trend line, which would misrepresent both periods).

A sustained period of high-mood entries ("rad") coincides with a positive personal life event. This pattern ends abruptly and is followed by a shift toward low-mood entries ("bad") coinciding with a separate, significant negative life event. Both transitions align closely enough in time to be more than coincidental, despite the small absolute entry counts for these mood categories.

## Clustering methodology

**Feature space.** Clustering is performed on **behavioral micro-activities only**. Two categories of tags are deliberately excluded from the clustering input (though retained in the full dataset for post-hoc interpretation):
- **Weather** (`sunny`, `clouds`, `rain`, etc.) : an environmental condition, not a behavior; including it would let two unrelated days appear artificially similar just by sharing weather.
- **Emotions** (`content`, `stressed`, `grateful`, etc.) : a granular, multi-select echo of the same signal as the held-out `mood` field. Including it would risk circular interpretation (a cluster "explained" by an emotion that was itself a clustering input).

This mirrors the original design principle — mood held out, used only to interpret clusters afterward — applied consistently to anything that functions as a proxy for mood, not just the `mood` field itself.

**Distance metric.** Because the activity matrix is binary and sparse, Jaccard distance was chosen over cosine or Hamming, as it best captures presence/absence similarity without being dominated by shared absences.

**Linkage & cut height.** Average-linkage hierarchical clustering, with cut heights chosen from the linkage matrix's own merge-distance gaps (largest jumps between consecutive merge heights) rather than arbitrary thresholds. As the dataset grew, additional well-separated gaps emerged, motivating a three-tier resolution rather than two:

- `cluster_fine` at t = 0.81 — most granular; used as a robustness check rather than a primary reporting tier, since very small clusters fragment further at this resolution.
- `cluster_main` at t = 0.90 — primary reporting tier; balances interpretability with stability.
- `cluster_coarse` at t = 0.95 — broadest split; used to test whether small clusters are genuinely distinct or merge away at low resolution.

Cluster labels assigned by the clustering algorithm are arbitrary integers that are **not stable across re-runs** — the same behavioral group can receive a different label number after re-running on updated data. Clusters are therefore always re-identified by their activity profile and member dates, never by an assumed label number.

## Findings

Hierarchical clustering on behavioral activity profiles (`cluster_main`, the primary reporting tier) revealed one dominant, high-frequency behavioral mode (n=983, ~98% of entries) alongside three small, behaviorally distinct clusters. This structure was confirmed stable across a full raw-data refresh (990 → 1000 entries): the dominant cluster and each small cluster's composition, activity profile, and member dates remained consistent, with only the finest-resolution tier showing minor turnover — consistent with very small clusters representing individually atypical days rather than recurring behavioral types.

The dominant cluster is characterized by routine, low-intensity activities: taking breaks, adequate sleep, focused work, cleaning, and social contact with friends.

The three small clusters were cross-referenced against calendar dates for interpretability:

- A 7-entry cluster (poor sleep, stress) aligns with several personally significant dates — anniversaries and a bereavement — though not all entries in this cluster have a confirmed explanation. This cluster was reproducible across the data refresh, with an identical activity profile and date set both times.
- A 7-entry cluster linked by seasonal weather tags (heat/humidity or clouds/tiredness) largely corresponds to summer and winter periods; several entries also coincide with scheduled appointments, which may confound the apparent weather effect and cannot be fully disentangled with the data as currently structured.
- A 3-entry cluster (happy, relaxed, grateful) corresponds to a short run of consecutive days shortly after a positive personal life event. Notably, this cluster remains distinct even at the broadest tested resolution (`cluster_coarse`), while every other small cluster merges into the dominant mode at that resolution — suggesting these days are unusually behaviorally distinct rather than a borderline case. This aligns with a separately observed pattern of high-mood ("rad") entries concentrated in the months following the same event.

## Known limitations

- Small clusters (n ≤ 7) are not statistically robust findings — they're best read as "notable individual days," not stable behavioral profiles.
- Cluster labels assigned by the algorithm are arbitrary and not stable across re-runs on updated data; all cluster-based findings in this document are anchored to activity profiles and specific dates, not label numbers (see methodology log for detail).
- Appointment-type events (e.g. therapy sessions) are not currently logged as a taggable activity, so their apparent association with certain clusters could only be identified manually and cannot yet be tested systematically.
- Weather/appointment confounding in some clusters cannot be resolved without additional data.
- The mood scale is heavily imbalanced: "good" (n=550) and "meh" (n=321) account for the large majority of entries, while "bad" (n=42), "rad" (n=43), and especially "awful" (n=3) are comparatively rare. 
- Heatmap rows and cluster interpretations involving underrepresented moods (particularly "awful") should be read as illustrative of individual entries rather than statistically stable patterns.

## Tooling split

- Python (notebook + scripts) — cleaning, EDA, plotting, clustering
- R (`analysis.R`) — optional deeper statistical contrasts
- SQL (via `moods.db`) — sanity checks, time-based aggregates

## Next steps

- Re-run the pipeline end-to-end with the `period` segmentation applied and compare pre/post cohorts.

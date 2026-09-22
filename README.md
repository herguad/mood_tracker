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
scripts/analysis.R          ─►  deeper stats / contrasts
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

### Pre/post period comparison

Aggregating mood and activity data by `period` (pre: n=774, post: n=226) confirms the pattern already suggested by individual date cross-referencing:

- **Mood distribution shifted sharply.** "Good" dropped from ~65% of entries (pre) to ~29% (post); "meh" more than doubled (~26% → ~63%); "rad" (the top of the mood scale), present in ~5% of pre-period entries, does not appear at all post; "bad" roughly doubled (~3% → ~7%); "awful" appears only in the post period. Every mood category shifted in the expected direction with no exceptions.
- **Overall activity structure remained comparatively stable.** Most macro-activity categories (emotions, sleep, weather, productivity, chores) shifted only slightly between periods. Two categories moved more notably: `social` activity increased (~46% → ~61%), while `health`-related activity decreased (~50% → ~42%) — suggesting the post-period was marked more by leaning toward social contact than by withdrawal, alongside some reduction in self-care-related activity.

**Caveat:** the "post" period (n=226) is considerably smaller than "pre" (n=774) — roughly one-quarter the size — reflecting that it covers a few months rather than the multi-year pre-period span. Percentages account for this size difference, but the smaller absolute sample means post-period figures should be read as indicative of a real, evident shift rather than as precisely estimated rates.

## Known limitations

- Small clusters (n ≤ 7) are not statistically robust findings — they're best read as "notable individual days," not stable behavioral profiles.
- Cluster labels assigned by the algorithm are arbitrary and not stable across re-runs on updated data; all cluster-based findings in this document are anchored to activity profiles and specific dates, not label numbers (see methodology log for detail).
- Appointment-type events (e.g. therapy sessions) are not currently logged as a taggable activity, so their apparent association with certain clusters could only be identified manually and cannot yet be tested systematically.
- Weather/appointment confounding in some clusters cannot be resolved without additional data.
- The mood scale is heavily imbalanced: "good" (n=550) and "meh" (n=321) account for the large majority of entries, while "bad" (n=42), "rad" (n=43), and especially "awful" (n=3) are comparatively rare. 
- Heatmap rows and cluster interpretations involving underrepresented moods (particularly "awful") should be read as illustrative of individual entries rather than statistically stable patterns.

### Mood transition analysis (R)

To test whether day-to-day mood changes follow a discernible pattern rather than occurring independently, a first-order mood transition analysis was performed in R.

**Method:** for each entry, the following day's mood was paired with the current day's mood (day-to-day pairs only; entries are excluded where no next-day mood exists). Transition frequencies were tabulated and converted to conditional probabilities (P(next mood | current mood)).

`awful` (n=3) was collapsed into `bad` prior to formal testing, as its sample size was too small to support reliable estimates in a 5-category contingency table.

**Findings:** transition probabilities show clear, non-uniform patterns — for example, "good" is followed by "good" 66.8% of the time (above its ~55% overall base rate, suggesting genuine day-to-day persistence rather than simple frequency), while "bad" most often transitions to "meh" (69.0%) rather than persisting or swinging to "good." Extreme-high ("rad") entries were never followed immediately by "bad," and vice versa.

**Statistical test:** a Pearson's chi-square test of independence on the collapsed 4-category transition table rejected the null hypothesis of independence (X² = 195.73, df = 9, p < 2.2e-16). Because several expected cell counts were small even after collapsing (R's built-in check flagged the chi-square approximation as potentially unreliable), this was corroborated with a simulation-based Fisher's exact test (10,000 replicates), which independently confirmed the result (p ≈ 0.0001 — the minimum resolvable value at this replicate count, indicating the observed pattern was more extreme than all 10,000 null-hypothesis simulations). Both tests support the same conclusion: mood on a given day is not independent of the previous day's mood.

### Association strength: mood vs. individual activities (R)

To identify which activities are most strongly linked to mood, Cramér's V (a standard measure of association strength for categorical variables, ranging 0–1) was computed between `mood` and each activity individually.

Emotion tags (e.g. `sad`, `happy`, `content`) were excluded from this comparison — as a granular, multi-select echo of the same signal as `mood` itself, they showed disproportionately high association values (up to 0.59) that reflect logging overlap rather than a genuine behavioral finding, consistent with the same reasoning applied to the clustering feature space.

Among behavioral, weather, and macro-category activities, associations were generally weak to moderate. Cramér's V does not correct for small sample size, and several high-looking values were found to be artifacts of very low activity frequency (e.g. `restaurant`, appearing in only 0.4% of entries, showed V = 0.221 despite too few observations to support a reliable estimate). Associations are therefore only reported for activities present in at least 5% of entries; activities below this threshold are flagged as unreliable rather than excluded outright.

The strongest reliable associations were: `good sleep` (V = 0.26), `date` (V = 0.24), `take a break` (V = 0.23), `medium sleep` (V = 0.22), `listen` (V = 0.20), the `productivity` and `social` macro categories (V ≈ 0.20 each), and `friends` (V = 0.19). Near-universal categories (`sleep`, `weather`, `emotions`, all logged in 97%+ of entries) showed correspondingly low association values, consistent with limited variance to associate with mood — the same ceiling effect observed earlier in the mood × macro-activity heatmap.

As with the earlier mood-transition analysis, these results describe association strength only, not causal direction — see the note on causal inference limitations below.

### Note on causal inference

The analyses above (Cramér's V, the mood transition tests, and the ordinal regression) establish **association**, not **causation**. This distinction matters for a few concrete reasons specific to this dataset:

- **No experimental manipulation.** This is purely observational, single-subject daily-diary data — no activity was randomly assigned, so any of these associations could reflect the reverse direction (mood influencing behavior, e.g. socializing more *because* one already feels good) rather than the direction implied by a predictive framing.
- **Confounding is likely and largely unaddressed.** Unmeasured factors (workload, external life events, weather beyond what's tagged) could independently drive both an activity and mood, producing an association between them without either causing the other.
- **Temporal precedence, while addressed for same-day autocorrelation (via the `mood_lag1` predictor), does not establish causal direction between same-day activities and same-day mood** — both are measured concurrently, so it remains possible mood shapes behavior rather than the reverse, or both stem from a shared prior cause.

Establishing genuine causal claims would require either an experimental/quasi-experimental design (e.g. tracking mood changes following a deliberate, isolated change in one activity) or more advanced causal inference methods (e.g. instrumental variables, structural causal models) that are out of scope for this project. The associations reported here are best read as **candidates for further, more rigorous investigation** — not as evidence that, for example, increasing social activity would improve mood.

### Ordinal logistic regression: mood and macro-category activities (R)

To assess whether macro-category activities predict mood while accounting for multiple factors simultaneously (rather than one at a time, as in the Cramér's V analysis), an ordinal logistic regression (`polr`, proportional odds model) was fit with `mood` as an ordered outcome (`awful < bad < meh < good < rad`).

Predictors were restricted to macro categories with meaningful variance — `health`, `social`, `better_me`, `productivity`, `chores`, and `period` — excluding `sleep`, `weather`, and `emotions`, which were logged in 97%+ of entries and showed correspondingly minimal association with mood in the Cramér's V analysis above.

**Accounting for day-to-day mood persistence.** Since the transition analysis had already established that mood is not independent from one day to the next, a second model added the previous day's mood (`mood_lag1`) as a predictor. A likelihood ratio test confirmed this substantially improved model fit (χ² = 95.1, df = 4, p < 0.001) — as expected, yesterday's mood strongly and linearly predicts today's mood (p < 0.001), with no meaningful non-linear pattern.

**Predictor results (from the model including `mood_lag1`):**

| Predictor | Direction | Significance |
|---|---|---|
| `social` | positive | p < 0.001 |
| `productivity` | positive | p < 0.001 |
| `better_me` | positive | p < 0.001 |
| `period` (pre vs. post) | positive (pre > post) | p < 0.001 |
| `chores` | positive | marginal (p ≈ 0.06) |
| `health` | positive | not significant (p ≈ 0.30) |

Critically, the `social`, `productivity`, and `better_me` associations remained essentially unchanged in size and significance after controlling for the previous day's mood — indicating these relationships are not simply an artifact of similar days clustering together in runs, and represent a more robust finding than the transition or Cramér's V analyses alone could establish.

`health` was not a significant predictor in either model, despite health-related activities being a defined macro category throughout this project — worth noting as a genuine null result rather than omitting it.

## Tooling split

- Python (notebook + scripts) — cleaning, EDA, plotting, clustering
- R (`analysis.R`) — optional deeper statistical contrasts
- SQL (via `moods.db`) — sanity checks, time-based aggregates


[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://moodtracker-7bhpym7ux3lh7dnjnthi4k.streamlit.app/)

# Methodology decisions log

A working record of technical/methodological issues found in this project and the reasoning behind each fix — kept separate from the polished README so the *why* isn't lost, and reusable as a checklist on future projects.

## 1. `load_db.py` used `if_exists="append"`

**Problem:** every re-run of the script duplicated all existing rows in the SQLite table, since nothing checked for or removed prior data first.

**Fix:** switched to `if_exists="replace"`. Since the cleaned CSV is always the full current dataset (not an incremental diff), the database should always mirror it exactly, not accumulate on top of it.

**Takeaway for future projects:** when a load step reads from a "full snapshot" file (not a log of new records), `replace` semantics are correct — `append` is only right when the *source* is itself incremental.

## 2. `mapping` dict (micro → macro categories) was defined but never applied

**Problem:** the 8-category mapping existed in code but wasn't used anywhere — `MultiLabelBinarizer` only ever ran on raw micro-activity labels, so the README's "8 categories" framing didn't match what the pipeline actually produced.

**Fix:** added a `macro_activities` column applying the mapping, then binarized it separately (`macro_df`) and merged alongside the micro binary columns.

**Takeaway:** when a script defines a mapping/lookup structure, grep for where it's actually *used* — an unused variable that looks load-bearing is an easy thing to miss in your own code, especially returning to it after a long gap.

## 3. Order-of-operations bug: cleanup ran after the mapping was applied

**Problem:** moving `mapping` and the `macro_activities` line earlier in the script (to also affect `moods_cleaned.csv`, not just the later features file) broke matching, because the activity-string cleanup (lowercasing, whitespace normalization) hadn't run yet at that point — so `mapping` was matching against unnormalized text.

**Fix:** reordered so cleanup → mapping → macro_activities creation, in that sequence, before the cleaned file is saved.

**Takeaway:** when relocating code, trace *data dependencies*, not just where a variable is used — a mapping dict depends on its input already being in the expected format, which may be established by a separate, earlier block.

## 4. `axis=1` deprecation in `.groupby()`

**Problem:** `micro_df.groupby(micro_df.columns, axis=1).max()` triggered a deprecation warning, then later became a hard `ValueError` after a pandas version update — same code, different behavior over time.

**Fix:** rewrote using a transpose instead: `micro_df.T.groupby(level=0).max().T` — groups on the (fully-supported) row axis instead of the deprecated column-axis groupby.

**Takeaway:** deprecation warnings are a countdown, not a suggestion — code that "still works" with a warning can silently break after an unrelated environment update (e.g. Colab auto-updating packages between sessions).

## 5. `moods_microacts.csv` was a stale, hand-made file, not a pipeline output

**Problem:** no script in the repo actually generated this file — it existed as a committed artifact from an earlier, informal stage of the project, and still contained mood/emotion words mixed in alongside real activities (confirmed: `content` was a genuine logged emotion tag, not a bug — but its presence in this *specific* file, unflagged as different from behavioral activities, was the actual problem).

**Fix:** added `micro_df.to_csv("data/moods_microacts.csv", index=False)` to `cleaning.py`, so the file is always regenerated from the current pipeline rather than existing as an untracked one-off.

**Takeaway:** any data file in a repo that isn't clearly *produced* by a script in that same repo is a liability — it can quietly drift out of sync with everything else and nobody notices until output looks wrong.

## 6. Feature space vs. interpretation variables — the weather/emotions exclusion

**Problem:** two categories of tags (weather, emotions) were included in the clustering feature space, even though the project's own design principle was to hold mood out of clustering and use it only afterward, to interpret cluster meaning. Weather is an environmental condition, not a behavior; emotions are a granular echo of the same signal as mood — including either risks either diluting genuine behavioral signal or producing circular findings.

**Fix:** excluded both from the array fed into the distance calculation (`X`), while keeping them in the full dataframe used afterward for cluster interpretation.

**Takeaway — the general principle, reusable beyond this project:** before clustering, explicitly separate *"things that define group membership"* from *"things used to explain what a group means afterward."* Anything that's really a proxy for your outcome variable belongs in the second category, not the first, even if it doesn't share the outcome variable's exact name.

## 7. Cut-height thresholds were reused across incompatible states of the data

**Problem:** `t=0.88`/`t=0.93` (and later `0.75`/`0.82`) were carried over from earlier runs without being re-derived — but the underlying distance matrix had changed each time (new raw data, then the mood-leak fix, then the weather/emotion exclusion). Reused thresholds on changed data are a guess, not a measurement.

**Fix:** switched to a data-driven approach — computing gaps between consecutive merge distances in the linkage matrix (`np.diff(Z[:, 2])`) and choosing cut heights that fall inside the largest gaps, so the choice is anchored to where the data naturally separates rather than an inherited number.

**Takeaway:** any threshold derived from a dataset needs to be re-derived whenever that dataset's underlying representation changes — not just when the row count changes, but when the *feature space* changes too (as it did here, twice).

## 8. A cluster comparison silently reused a stale variable

**Problem:** after re-clustering a "core" subset (`Z_core`), only `clusters_coarse` was recomputed — `clusters_main` still held its value from the *original*, full-dataset clustering. This produced a length mismatch (caught before running, this time) between the stale array and the core-only dataframe it was about to be assigned to.

**Fix:** added back the missing `clusters_main = fcluster(Z_core, ...)` line.

**Takeaway:** when re-deriving one of two parallel variables (e.g. main/coarse, fine/broad), explicitly re-check both — a script that "runs" isn't the same as a script that's internally consistent; a shape/length mismatch is one of the few bugs Python will catch for you, but a silently-stale-but-same-shape variable often won't be caught at all.

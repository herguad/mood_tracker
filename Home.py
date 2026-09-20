import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mood Tracker | Narrative", layout="wide")

@st.cache_data
def load_data():
    df_feats = pd.read_csv("data/moods_features.csv")
    df_cleaned = pd.read_csv("data/moods_cleaned.csv")
    return df_feats, df_cleaned

df_feats, df_cleaned = load_data()

st.title("Mood Tracker: A Data Analysis & ML Project")

st.markdown("""
A one-page narrative summary. Use the sidebar to explore the EDA, clustering,
and statistical findings behind each point in more detail.
""")

import plotly.express as px

# --- Key finding 1: mood distribution is imbalanced ---
st.header("1. Mood is heavily skewed toward 'good' and 'meh'")

mood_order = ["awful", "bad", "meh", "good", "rad"]
mood_counts = df_feats["mood"].value_counts().reindex(mood_order).reset_index()
mood_counts.columns = ["mood", "count"]

fig1 = px.bar(mood_counts, x="mood", y="count", title="Mood Frequency Distribution")
st.plotly_chart(fig1, width="stretch")

st.markdown("""
Entries skew heavily toward **good** (55%) and **meh** (32%), with **bad**, **rad**,
and especially **awful** (n=3) comparatively rare — findings involving these
underrepresented moods should be read as illustrative rather than statistically robust.
""")

# --- Key finding 2: the pre/post period shift ---
st.header("2. A clear pre/post shift follows a significant life event")

mood_by_period = (
    df_feats.groupby("period")["mood"]
    .value_counts(normalize=True)
    .unstack(fill_value=0)
    .reindex(["pre", "post"])
    .reindex(columns=mood_order)
    * 100
)
mood_by_period_long = mood_by_period.reset_index().melt(
    id_vars="period", var_name="mood", value_name="percentage"
)

fig2 = px.bar(
    mood_by_period_long, x="mood", y="percentage", color="period",
    barmode="group", title="Mood Distribution: Pre vs. Post Period",
    color_discrete_map={"pre": "#1f77b4", "post": "#ff7f0e"}
)
st.plotly_chart(fig2, width="stretch")

pre_n = (df_feats["period"] == "pre").sum()
post_n = (df_feats["period"] == "post").sum()

st.markdown(f"""
Comparing entries before and after a significant personal life event (pre: n={pre_n},
post: n={post_n}), mood shifted sharply: **good** dropped from ~65% to ~29% of entries,
**meh** more than doubled, and **rad** — the top of the mood scale — disappeared
entirely post-event. Activity patterns shifted too: social activity *increased*
(~46% → ~61%) while health-related activity *decreased* (~50% → ~42%), suggesting
a lean toward social contact rather than withdrawal.

*Note: the post-period sample (n={post_n}) is considerably smaller than pre (n={pre_n}),
so percentages should be read as indicative of a real shift rather than precisely
estimated rates.*
""")

# --- Key finding 3: clustering surfaced a grief-linked behavioral cluster ---
st.header("3. Clustering surfaced a small, distinct 'grief cluster'")

@st.cache_data
def load_clusters():
    return pd.read_csv("data/cluster_assignments.csv")

df_clusters = load_clusters()

cluster_sizes = df_clusters["cluster_main"].value_counts().sort_values(ascending=False).reset_index()
cluster_sizes.columns = ["cluster", "n_entries"]
cluster_sizes["cluster"] = cluster_sizes["cluster"].astype(str)

col1, col2 = st.columns(2)

with col1:
    fig3a = px.bar(cluster_sizes, x="cluster", y="n_entries",
                    category_orders={"cluster": cluster_sizes["cluster"].tolist()},
                    title="All Clusters")
    fig3a.update_xaxes(type="category")
    st.plotly_chart(fig3a, width="stretch")

with col2:
    small_clusters = cluster_sizes[cluster_sizes["n_entries"] < 50]
    fig3b = px.bar(small_clusters, x="cluster", y="n_entries",
                    category_orders={"cluster": small_clusters["cluster"].tolist()},
                    title="Small Clusters (Detail)", text="n_entries")
    fig3b.update_traces(textposition="outside")
    fig3b.update_xaxes(type="category")
    st.plotly_chart(fig3b, width="stretch")

st.markdown("""
Hierarchical clustering on behavioral activity profiles (Jaccard distance, average
linkage) revealed one dominant behavioral mode (~98% of entries) alongside three
small, distinct clusters. One — characterized by poor sleep and stress — aligns with
several personally significant dates and was confirmed stable across a full raw-data
refresh. See the **Clustering** page for full profiles and methodology.
""")

# --- Key finding 4: mood is not random day-to-day ---
st.header("4. Mood is statistically predictable from the previous day")

st.markdown("""
A first-order mood transition analysis (R) found that mood on a given day is
**not independent** of the previous day's mood (chi-square test of independence,
p < 0.001; confirmed with a simulation-based Fisher's exact test as a robustness
check for small sample cells). For example, a "good" day is followed by another
"good" day 66.8% of the time — well above chance — while "bad" days most often
recover to "meh" (69.0%) rather than persisting.

An ordinal regression confirmed this pattern holds even after accounting for
specific activities: **social**, **productivity**, and **better_me** activity levels
remained significantly associated with same-day mood even after controlling for
the previous day's mood — indicating these relationships aren't simply an artifact
of similar days clustering together.

*These findings describe statistical association, not causation — see the
**Statistical Findings** page for full detail and the causal inference note.*

See the **Statistical Findings** page for the full transition matrix, association
rankings, and regression results.
""")

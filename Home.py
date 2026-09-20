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
st.write("Placeholder: cluster size summary + link/pointer to Clustering page for detail.")

# --- Key finding 4: mood is not random day-to-day ---
st.header("4. Mood is statistically predictable from the previous day")
st.write("Placeholder: one-line transition-analysis result + pointer to Statistical Findings page.")

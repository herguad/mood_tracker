import streamlit as st
import pandas as pd
import plotly.express as px

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from style import apply_custom_style

st.set_page_config(page_title="Clustering", layout="wide")
apply_custom_style()

@st.cache_data
def load_data():
    df_feats = pd.read_csv("data/moods_features.csv")
    df_clusters = pd.read_csv("data/cluster_assignments.csv")
    return df_feats, df_clusters

df_feats, df_clusters = load_data()

st.title("Behavioral Clustering")

st.markdown("""
Clustering was performed on behavioral micro-activities only — weather and emotion
tags were excluded, since weather is environmental rather than behavioral, and
emotion tags are a granular echo of the mood field itself. Pairwise **Jaccard
distance** was used (suited to binary, sparse activity data), with **average-linkage
hierarchical clustering**. Cut heights were chosen from the largest gaps in the
linkage matrix's merge distances, rather than arbitrary thresholds, at three
resolutions — `fine`, `main` (the primary reporting tier), and `coarse`.
""")

macro_cols = ["emotions", "sleep", "health", "social", "better_me", "productivity", "chores", "weather"]
weather_micro = ["sunny", "clouds", "rain", "storm", "wind", "heat", "humid", "cold"]
emotion_micro = ["happy", "excited", "grateful", "relaxed", "content", "tired", "unsure",
                  "bored", "anxious", "angry", "stressed", "sad", "desperate", "irritated"]
all_micro_cols = [c for c in df_feats.columns if c not in macro_cols
                   and c not in ["mood", "full_date", "period", "weekday"]]

# Join cluster labels onto full activity data (index-aligned, same source dataframe)
df_joined = df_feats.copy()
df_joined["cluster_main"] = df_clusters["cluster_main"].values

st.header("Cluster sizes")
cluster_sizes = df_joined["cluster_main"].value_counts().sort_values(ascending=False).reset_index()
cluster_sizes.columns = ["cluster", "n_entries"]
cluster_sizes["cluster"] = cluster_sizes["cluster"].astype(str)

col1, col2 = st.columns(2)
with col1:
    fig_all = px.bar(cluster_sizes, x="cluster", y="n_entries",
                      category_orders={"cluster": cluster_sizes["cluster"].tolist()},
                      title="All Clusters")
    fig_all.update_xaxes(type="category")
    st.plotly_chart(fig_all, width="stretch")

with col2:
    small = cluster_sizes[cluster_sizes["n_entries"] < 50]
    fig_small = px.bar(small, x="cluster", y="n_entries",
                        category_orders={"cluster": small["cluster"].tolist()},
                        title="Small Clusters (Detail)", text="n_entries")
    fig_small.update_traces(textposition="outside")
    fig_small.update_xaxes(type="category")
    st.plotly_chart(fig_small, width="stretch")

st.header("Explore a cluster's activity profile")
cluster_options = sorted(df_joined["cluster_main"].unique())
selected_cluster = st.selectbox("Select a cluster", cluster_options)

cluster_subset = df_joined[df_joined["cluster_main"] == selected_cluster]
n = len(cluster_subset)
top_activities = cluster_subset[all_micro_cols].sum().sort_values(ascending=False).head(10).reset_index()
top_activities.columns = ["activity", "count"]

st.write(f"Cluster {selected_cluster} — {n} entries")
fig_cluster = px.bar(top_activities, x="activity", y="count",
                      title=f"Top activities in cluster {selected_cluster}")
fig_cluster.update_xaxes(type="category")
st.plotly_chart(fig_cluster, width="stretch")

st.header("The grief-linked cluster")
st.markdown("""
One small, consistently reproducible cluster is characterized by poor sleep and
stress. Several of its entries align with personally significant dates — anniversaries
and a bereavement — though not all entries in this cluster have a confirmed
explanation. This finding was confirmed stable after a full raw-data refresh: the
same cluster reappeared with an identical activity profile and dates, despite
receiving a different (arbitrary) label on re-run — cluster labels are not stable
identifiers across re-runs, so clusters are always re-identified by content, not by
number.
""")
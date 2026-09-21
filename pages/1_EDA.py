import streamlit as st
import pandas as pd
import plotly.express as px

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from style import apply_custom_style

st.set_page_config(page_title="EDA", layout="wide")
apply_custom_style()

@st.cache_data
def load_data():
    df_feats = pd.read_csv("data/moods_features.csv")
    activity_mapping = pd.read_csv("data/activity_mapping.csv")
    return df_feats, activity_mapping

df_feats, activity_mapping = load_data()

st.title("Exploratory Data Analysis")

macro_cols = ["emotions", "sleep", "health", "social", "better_me", "productivity", "chores", "weather"]
weather_micro = ["sunny", "clouds", "rain", "storm", "wind", "heat", "humid", "cold"]
emotion_micro = ["happy", "excited", "grateful", "relaxed", "content", "tired", "unsure",
                  "bored", "anxious", "angry", "stressed", "sad", "desperate", "irritated"]
all_micro_cols = [c for c in df_feats.columns if c not in macro_cols
                   and c not in ["mood", "full_date", "period", "weekday"]]
behavioral_micro = [c for c in all_micro_cols if c not in weather_micro and c not in emotion_micro]

# --- Macro-activity frequency ---
st.header("Macro-activity frequency")
macro_counts = df_feats[macro_cols].sum().sort_values(ascending=False).reset_index()
macro_counts.columns = ["category", "count"]
fig_macro = px.bar(macro_counts, x="category", y="count", title="Macro-activity Frequency")
fig_macro.update_xaxes(type="category")
st.plotly_chart(fig_macro, width="stretch")

# --- Macro -> micro drill-down ---
st.subheader("Explore micro-activities within a category")
selected_macro = st.selectbox("Select a macro category", macro_cols)

micro_in_category = activity_mapping.loc[
    activity_mapping["macro_category"] == selected_macro, "micro_activity"
].tolist()
micro_in_category = [c for c in micro_in_category if c in df_feats.columns]

if micro_in_category:
    drill_counts = df_feats[micro_in_category].sum().sort_values(ascending=False).reset_index()
    drill_counts.columns = ["activity", "count"]
    fig_drill = px.bar(drill_counts, x="activity", y="count",
                        title=f"Top micro-activities in '{selected_macro}'")
    fig_drill.update_xaxes(type="category")
    st.plotly_chart(fig_drill, width="stretch")
else:
    st.write("No mapped micro-activities found for this category.")

# --- Weather and emotion tags ---
st.header("Weather and emotion tags")
col1, col2 = st.columns(2)

with col1:
    weather_counts = df_feats[weather_micro].sum().sort_values(ascending=False).reset_index()
    weather_counts.columns = ["tag", "count"]
    fig_weather = px.bar(weather_counts, x="tag", y="count", title="Weather Tag Frequency")
    fig_weather.update_xaxes(type="category")
    st.plotly_chart(fig_weather, width="stretch")

with col2:
    emotion_counts = df_feats[emotion_micro].sum().sort_values(ascending=False).reset_index()
    emotion_counts.columns = ["tag", "count"]
    fig_emotion = px.bar(emotion_counts, x="tag", y="count", title="Emotion Tag Frequency")
    fig_emotion.update_xaxes(type="category")
    st.plotly_chart(fig_emotion, width="stretch")

st.caption("""
Weather and emotion tags are shown separately from behavioral activities: weather
is environmental rather than behavioral, and emotion tags are a granular echo of
the mood field itself — both were excluded from clustering for the same reason.
""")

# --- Heatmaps ---
st.header("Mood × activity heatmaps")

mood_order = ["awful", "bad", "meh", "good", "rad"]

behavioral_counts = df_feats[behavioral_micro].sum().sort_values(ascending=False)
top_behavioral = behavioral_counts.head(15).index.tolist()

mood_micro = df_feats.groupby("mood")[top_behavioral].mean().reindex(mood_order)
fig_heat_micro = px.imshow(mood_micro, aspect="auto", color_continuous_scale="viridis",
                             title="Mood × Behavioral Micro-activity Presence Rate")
st.plotly_chart(fig_heat_micro, width="stretch")

mood_macro = df_feats.groupby("mood")[macro_cols].mean().reindex(mood_order)
fig_heat_macro = px.imshow(mood_macro, aspect="auto", color_continuous_scale="viridis",
                             title="Mood × Macro-activity Presence Rate")
st.plotly_chart(fig_heat_macro, width="stretch")

st.caption("""
'emotions' and 'weather' appear near-ceiling across all moods (logged in 97%+ of
entries), reflecting limited variance rather than a genuine mood association —
read the other six macro columns as the more informative ones above.
""")
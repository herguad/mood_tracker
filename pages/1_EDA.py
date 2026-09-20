import streamlit as st
import pandas as pd

st.set_page_config(page_title="EDA", layout="wide")

from style import apply_custom_style
apply_custom_style()

@st.cache_data
def load_data():
    return pd.read_csv("data/moods_features.csv")

df_feats = load_data()

st.title("Exploratory Data Analysis")

macro_cols = ["emotions", "sleep", "health", "social", "better_me", "productivity", "chores", "weather"]

st.header("Macro-activity frequency")
st.write("Placeholder: macro bar chart.")

st.subheader("Explore micro-activities within a category")
selected_macro = st.selectbox("Select a macro category", macro_cols)
st.write(f"Placeholder: top micro-activities driving '{selected_macro}'.")

st.header("Weather and emotion tags")
st.write("Placeholder: separate weather/emotion frequency charts, per the behavioral/weather/emotion split.")

st.header("Mood × activity heatmaps")
st.write("Placeholder: behavioral and macro heatmaps.")

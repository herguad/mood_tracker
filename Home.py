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

# --- Key finding 1: mood distribution is imbalanced ---
st.header("1. Mood is heavily skewed toward 'good' and 'meh'")
st.write("Placeholder: mood frequency bar chart + brief narrative text.")

# --- Key finding 2: the pre/post period shift ---
st.header("2. A clear pre/post shift follows a significant life event")
st.write("Placeholder: mood-by-period comparison chart + brief narrative text.")

# --- Key finding 3: clustering surfaced a grief-linked behavioral cluster ---
st.header("3. Clustering surfaced a small, distinct 'grief cluster'")
st.write("Placeholder: cluster size summary + link/pointer to Clustering page for detail.")

# --- Key finding 4: mood is not random day-to-day ---
st.header("4. Mood is statistically predictable from the previous day")
st.write("Placeholder: one-line transition-analysis result + pointer to Statistical Findings page.")

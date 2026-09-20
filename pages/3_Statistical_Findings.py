import streamlit as st
import pandas as pd

st.set_page_config(page_title="Statistical Findings", layout="wide")

from style import apply_custom_style
apply_custom_style()

st.title("Statistical Findings (R)")

st.header("Mood transition patterns")
st.write("Placeholder: transition probability heatmap + chi-square/Fisher's result summary.")

st.header("Association strength (Cramer's V)")
st.write("Placeholder: ranked bar chart of reliable associations, with the <5%-frequency exclusion noted.")

st.header("Ordinal regression")
st.write("Placeholder: significant predictors table + the lagged-mood model comparison result.")

st.warning("These findings describe association, not causation — see the README's causal inference note for detail.")

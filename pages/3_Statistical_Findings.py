import streamlit as st
import pandas as pd
import plotly.express as px

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from style import apply_custom_style

st.set_page_config(page_title="Statistical Findings", layout="wide")
apply_custom_style()

@st.cache_data
def load_data():
    transitions = pd.read_csv("data/mood_transition_probs.csv")
    cramers = pd.read_csv("data/cramers_v_results.csv")
    return transitions, cramers

transitions, cramers = load_data()
mood_order = ["awful", "bad", "meh", "good", "rad"]

st.title("Statistical Findings (R)")

st.header("Mood transition patterns")
st.markdown("""
A first-order transition analysis found that mood is **not independent** from one
day to the next (chi-square test of independence, p < 0.001; confirmed with a
simulation-based Fisher's exact test to account for small sample cells after
collapsing the rare "awful" category into "bad").
""")

transition_pivot = transitions.pivot(index="mood", columns="next_mood", values="prob").reindex(
    index=mood_order, columns=mood_order
)
fig_trans = px.imshow(
    transition_pivot, aspect="auto", color_continuous_scale="viridis",
    text_auto=".0%", title="Mood Transition Probabilities: P(next mood | current mood)"
)
st.plotly_chart(fig_trans, width="stretch")

st.header("Association strength (Cramér's V)")
st.markdown("""
Emotion tags were excluded from this comparison, as a granular echo of the mood
field itself. Associations from activities logged in fewer than 5% of entries are
flagged as unreliable — Cramér's V does not correct for small sample size.
""")

cramers_reliable = cramers[cramers["reliable"]].sort_values("cramers_v", ascending=False).head(15)
fig_cramers = px.bar(cramers_reliable, x="activity", y="cramers_v",
                      title="Strongest Reliable Associations with Mood")
fig_cramers.update_xaxes(type="category")
st.plotly_chart(fig_cramers, width="stretch")

with st.expander("Show excluded (low-frequency) associations"):
    unreliable = cramers[~cramers["reliable"]].sort_values("cramers_v", ascending=False)
    st.dataframe(unreliable, width="stretch")

st.header("Ordinal regression")
st.markdown("""
An ordinal logistic regression tested whether macro-category activities predict
mood, accounting for multiple factors simultaneously. A lagged mood predictor was
added to account for the day-to-day persistence shown above — critically, `social`,
`productivity`, and `better_me` remained significant predictors of same-day mood
even after controlling for the previous day's mood, indicating these associations
are not simply an artifact of similar days clustering together.
""")

regression_summary = pd.DataFrame({
    "Predictor": ["social", "productivity", "better_me", "period (pre vs. post)", "chores", "health"],
    "Direction": ["positive", "positive", "positive", "positive (pre > post)", "positive", "positive"],
    "Significance": ["p < 0.001", "p < 0.001", "p < 0.001", "p < 0.001", "marginal (p ≈ 0.06)", "not significant (p ≈ 0.30)"]
})
st.dataframe(regression_summary, width="stretch", hide_index=True)

st.warning("""
**These findings describe association, not causation.** This is purely observational,
single-subject data — no activity was randomly assigned, so any of these associations
could reflect the reverse direction (mood influencing behavior) or a shared,
unmeasured confounder, rather than the direction implied by a predictive framing.
""")
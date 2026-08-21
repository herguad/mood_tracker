import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df_feats = pd.read_csv("data/moods_features.csv")

df_feats.info()
df_feats.describe(include="all")

#Time coverage
df = pd.read_csv("data/moods_cleaned.csv")

df["full_date"] = pd.to_datetime(df["full_date"])

daily_counts = (
    df.groupby("full_date")
      .size()
      .rename("entries")
)

plt.figure(figsize=(12, 4))
plt.plot(daily_counts.index, daily_counts.values)

plt.title("Mood Tracking Coverage Over Time")
plt.xlabel("Date")
plt.ylabel("Number of Entries")

plt.tight_layout()
plt.show()


# Rolling avg for daily_counts

rolling = daily_counts.rolling(window=7).mean()

plt.figure(figsize=(12, 4))
plt.plot(daily_counts.index, daily_counts.values, label="Daily entries")
plt.plot(rolling.index, rolling.values, label="7-day rolling average")

plt.title("Mood Tracking Coverage Over Time")
plt.xlabel("Date")
plt.ylabel("Number of Entries")
plt.legend()

plt.tight_layout()
plt.show()

#Mood counts
mood_counts = df["mood"].value_counts()

plt.figure(figsize=(8, 4))
plt.bar(mood_counts.index, mood_counts.values)

plt.title("Mood Frequency Distribution")
plt.xlabel("Mood")
plt.ylabel("Number of Entries")

plt.tight_layout()
plt.show()

# In %
mood_pct = mood_counts / mood_counts.sum() * 100

plt.figure(figsize=(8, 4))
plt.bar(mood_pct.index, mood_pct.values)

plt.title("Mood Distribution (Percentage)")
plt.xlabel("Mood")
plt.ylabel("Percentage of Entries")

plt.tight_layout()
plt.show()


#Activity frequency
#Which activities dominate the dataset? Split micro vs. macro so they don't mix in the same plot.

macro_cols = ["emotions", "sleep", "health", "social", "better_me", "productivity", "chores", "weather"]
micro_cols = [c for c in df_feats.columns if c not in macro_cols and c not in ["mood", "full_date", "period", "weekday"]]

micro_counts = df_feats[micro_cols].sum().sort_values(ascending=False)
macro_counts = df_feats[macro_cols].sum().sort_values(ascending=False)

n_entries = len(df_feats)

#Micro-activity frequency
plt.figure(figsize=(10, 5))
plt.bar(micro_counts.index, micro_counts.values, color="green")

plt.title("Micro-activity Frequency across Mood Entries")
plt.xlabel("Micro Activity")
plt.ylabel("Number of Entries")

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

#Micro-activity frequency in %
micro_pct = (micro_counts / n_entries) * 100

plt.figure(figsize=(10, 5))
plt.bar(micro_pct.index, micro_pct.values)

plt.title("Micro-activity Frequency (% of Mood Entries)")
plt.xlabel("Micro Activity")
plt.ylabel("Percentage of Entries")

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

#Macro-activity frequency
plt.figure(figsize=(10, 5))
plt.bar(macro_counts.index, macro_counts.values, color="mediumvioletred")

plt.title("Macro-activity Frequency across Mood Entries")
plt.xlabel("Macro Activity")
plt.ylabel("Number of Entries")

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

#Macro-activity frequency in %
macro_pct = (macro_counts / n_entries) * 100

plt.figure(figsize=(10, 5))
plt.bar(macro_pct.index, macro_pct.values)

plt.title("Macro-activity Frequency (% of Mood Entries)")
plt.xlabel("Macro Activity")
plt.ylabel("Percentage of Entries")

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()


#Heatmaps

#Mood vs Micro-activity, normalized — top 15 micro activities only, for readability
heatmap_micro_df = df_feats[["mood"] + micro_cols]
mood_micro = heatmap_micro_df.groupby("mood").mean()
top_micro = micro_counts.head(15).index
mood_micro = mood_micro[top_micro]

plt.figure(figsize=(12, 6))
sns.heatmap(
    mood_micro,
    cmap="viridis",
    cbar_kws={"label": "Activity Presence Rate"}
)

plt.title("Mood vs Micro-activity Presence Rate")
plt.xlabel("Micro Activity")
plt.ylabel("Mood")

plt.tight_layout()
plt.show()

#Mood vs Macro-activity, normalized — all 8 categories, no truncation needed
heatmap_macro_df = df_feats[["mood"] + macro_cols]
mood_macro = heatmap_macro_df.groupby("mood").mean()

plt.figure(figsize=(10, 6))
sns.heatmap(
    mood_macro,
    cmap="viridis",
    cbar_kws={"label": "Activity Presence Rate"}
)

plt.title("Mood vs Macro-activity Presence Rate")
plt.xlabel("Macro Activity")
plt.ylabel("Mood")

plt.tight_layout()
plt.show()
import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("imgs", exist_ok=True)

df_feats = pd.read_csv("data/moods_features.csv")

macro_cols = ["emotions", "sleep", "health", "social", "better_me", "productivity", "chores", "weather"]

weather_micro = ["sunny", "clouds", "rain", "storm", "wind", "heat", "humid", "cold"]
emotion_micro = ["happy", "excited", "grateful", "relaxed", "content", "tired", "unsure",
                 "bored", "anxious", "angry", "stressed", "sad", "desperate", "irritated"]

all_micro_cols = [c for c in df_feats.columns if c not in macro_cols and c not in ["mood", "full_date", "period", "weekday"]]
behavioral_micro = [c for c in all_micro_cols if c not in weather_micro and c not in emotion_micro]

# 1. Entry counts per period
print("=== Entries per period ===")
print(df_feats["period"].value_counts())

# 2. Mood distribution, pre vs. post (normalized — periods differ in size)
print("\n=== Mood distribution by period (%) ===")
mood_by_period = df_feats.groupby("period")["mood"].value_counts(normalize=True).unstack(fill_value=0) * 100
mood_by_period = mood_by_period.reindex(["pre", "post"])
print(mood_by_period)

# 3. Macro-activity frequency, pre vs. post
print("\n=== Macro-activity frequency by period (%) ===")
macro_by_period = df_feats.groupby("period")[macro_cols].mean() * 100
macro_by_period = macro_by_period.reindex(["pre", "post"])
print(macro_by_period)

# 4. Behavioral micro-activity frequency, pre vs. post — sorted by largest shift
print("\n=== Behavioral micro-activity frequency by period (%), sorted by shift ===")
behavioral_by_period = df_feats.groupby("period")[behavioral_micro].mean().T * 100
behavioral_by_period["difference"] = behavioral_by_period["post"] - behavioral_by_period["pre"]
behavioral_by_period = behavioral_by_period.sort_values("difference")
print(behavioral_by_period)

# Plot: mood distribution comparison
mood_by_period.T.plot(kind="bar", figsize=(8, 5))
plt.title("Mood Distribution: Pre vs. Post Period")
plt.xlabel("Mood")
plt.ylabel("Percentage of Entries")
plt.legend(title="Period")
plt.tight_layout()
plt.savefig("imgs/mood_by_period.png", dpi=150)
plt.show()

# Plot: macro-activity comparison
macro_by_period.T.plot(kind="bar", figsize=(10, 5))
plt.title("Macro-activity Frequency: Pre vs. Post Period")
plt.xlabel("Macro Activity")
plt.ylabel("Percentage of Entries")
plt.legend(title="Period")
plt.tight_layout()
plt.savefig("imgs/macro_by_period.png", dpi=150)
plt.show()
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


#Activity frequency
#Which activities dominate the dataset?
#Micro is split three ways — genuine behaviors, weather, and emotion tags —
#since weather/emotions are near-universal and would otherwise dominate
#a combined ranking (e.g. crowding out real behaviors from a "top 15" list).

macro_cols = ["emotions", "sleep", "health", "social", "better_me", "productivity", "chores", "weather"]

weather_micro = ["sunny", "clouds", "rain", "storm", "wind", "heat", "humid", "cold"]
emotion_micro = ["happy", "excited", "grateful", "relaxed", "content", "tired", "unsure",
                 "bored", "anxious", "angry", "stressed", "sad", "desperate", "irritated"]

all_micro_cols = [c for c in df_feats.columns if c not in macro_cols and c not in ["mood", "full_date", "period", "weekday"]]
behavioral_micro = [c for c in all_micro_cols if c not in weather_micro and c not in emotion_micro]
weather_micro = [c for c in weather_micro if c in all_micro_cols]
emotion_micro = [c for c in emotion_micro if c in all_micro_cols]

behavioral_counts = df_feats[behavioral_micro].sum().sort_values(ascending=False)
weather_counts = df_feats[weather_micro].sum().sort_values(ascending=False)
emotion_counts = df_feats[emotion_micro].sum().sort_values(ascending=False)
macro_counts = df_feats[macro_cols].sum().sort_values(ascending=False)

#Behavioral micro-activity frequency
plt.figure(figsize=(10, 5))
plt.bar(behavioral_counts.index, behavioral_counts.values, color="green")

plt.title("Behavioral Micro-activity Frequency Across Mood Entries")
plt.xlabel("Micro Activity")
plt.ylabel("Number of Entries")

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

#Weather micro-activity frequency
plt.figure(figsize=(8, 4))
plt.bar(weather_counts.index, weather_counts.values, color="steelblue")

plt.title("Weather Tag Frequency Across Mood Entries")
plt.xlabel("Weather Tag")
plt.ylabel("Number of Entries")

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

#Emotion micro-activity frequency
plt.figure(figsize=(10, 4))
plt.bar(emotion_counts.index, emotion_counts.values, color="darkorange")

plt.title("Emotion Tag Frequency Across Mood Entries")
plt.xlabel("Emotion Tag")
plt.ylabel("Number of Entries")

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

#Macro-activity frequency
plt.figure(figsize=(10, 5))
plt.bar(macro_counts.index, macro_counts.values, color="mediumvioletred")

plt.title("Macro-activity Frequency Across Mood Entries")
plt.xlabel("Macro Activity")
plt.ylabel("Number of Entries")

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()


#Heatmaps

#Mood vs behavioral micro-activity, normalized: 
# top 15 BEHAVIORAL activities only
#(ranking now excludes weather/emotion tags, so it can't be crowded out by them)
heatmap_micro_df = df_feats[["mood"] + behavioral_micro]
mood_micro = heatmap_micro_df.groupby("mood").mean()
top_behavioral = behavioral_counts.head(15).index
mood_micro = mood_micro[top_behavioral]

plt.figure(figsize=(12, 6))
sns.heatmap(
    mood_micro,
    cmap="viridis",
    cbar_kws={"label": "Activity Presence Rate"}
)

plt.title("Mood × Behavioral Micro-activity Presence Rate")
plt.xlabel("Micro Activity")
plt.ylabel("Mood")

plt.tight_layout()
plt.show()

#Mood vs Macro-activity, normalized: all 8 categories
#Note: "emotions" and "weather" are near-universal (~97-99% of entries) 
# by construction, so they'll appear near-ceiling regardless of mood
# read the other 6 columns 
# as the more informative ones in this heatmap.
heatmap_macro_df = df_feats[["mood"] + macro_cols]
mood_macro = heatmap_macro_df.groupby("mood").mean()

plt.figure(figsize=(10, 6))
sns.heatmap(
    mood_macro,
    cmap="viridis",
    cbar_kws={"label": "Activity Presence Rate"}
)

plt.title("Mood × Macro-activity Presence Rate")
plt.xlabel("Macro Activity")
plt.ylabel("Mood")

plt.tight_layout()
plt.show()

# In the behavioural heatmap, "awful" shows no gradient values.
# Check that the sample size is skewing the average towards extremes.

print(mood_counts)
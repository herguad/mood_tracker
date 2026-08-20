import pandas as pd
import numpy as np
import re
import ast
from sklearn.preprocessing import MultiLabelBinarizer


# Load raw data
df = pd.read_csv("data/raw_mood.csv")

#print(df.columns)

# Standardize column names
df.columns = [c.strip().lower() for c in df.columns]

print(df.columns)

# Parse dates safely
df["full_date"] = pd.to_datetime(df["full_date"], errors="coerce")

# Drop rows with invalid or missing mood/date
df = df.dropna(subset=["full_date", "mood"])

# Identify structural break to later nalyze as separate cohort.
CUTOFF = "2026-02-01"
df["period"] = np.where(df["full_date"] < CUTOFF, "pre", "post")

# Normalize mood text (remove emojis, lowercase, strip)
def normalize_mood(m):
    m = m.lower().strip()
    m = re.sub(r"[^\w\s]", "", m)  # remove punctuation
    return m

df["mood"] = df["mood"].apply(normalize_mood)

df["weekday"] = pd.to_datetime(df["full_date"]).dt.day_name()

# Clean notes if present
if "note" in df.columns:
    def clean_text(t):
        if pd.isna(t): return ""
        t = str(t).lower()
        t = re.sub(r"http\S+", "", t)
        t = re.sub(r"\s+", " ", t)
        t = re.sub(r"[^\w\s.,!?]", "", t)
        return t.strip()
    df["note"] = df["note"].apply(clean_text)


# Remove NaN columns and subdivide 'activities' into 8 categories: emotions,sleep, health, social, better me, productivity, chores and weather.

# 1. Drop unwanted columns
df = df.drop(columns=["date", "time", "scales", "note_title", "note"], errors="ignore")

print(df.head())

# 2. Ensure 'activities' column contains actual lists
print(type(df.activities))

# Change | for commas in activities column to get lists instead of single strings.
df['activities']=df['activities'].str.split('|')
print(type(df.activities[5]))
print(df.activities[6])

#Clean trailing spaces in decomposed micro_activities column names. Normalize.
df["activities"] = df["activities"].apply(
    lambda lst: [
        re.sub(r"\s+", " ", item)   # collapse internal spaces
          .strip()                  # remove left/right spaces
          .lower()                  # normalize case
        for item in lst
    ]
)

# Map labels into the 8 categories.
mapping = {
    "happy": "emotions",
    "excited": "emotions",
    "grateful": "emotions",
    "relaxed": "emotions",
    "content": "emotions",
    "tired": "emotions",
    "unsure": "emotions",
    "bored": "emotions",
    "anxious": "emotions",
    "angry": "emotions",
    "stressed": "emotions",
    "sad": "emotions",
    "desperate": "emotions",
    "irritated": "emotions",
    "happy": "emotions",
    "early": "sleep",
    "good": "sleep",
    "medium": "sleep",
    "bad": "sleep",
    "good sleep": "sleep",
    "bad sleep": "sleep",
    "medium sleep": "sleep",
    "sleep early": "sleep",
    "excercise": "health",
    "exercise": "health",
    "drink water": "health",
    "walk": "health",
    "stretch": "health",
    "doctor": "health",
    "eat healthy": "health",
    "no meat": "health",
    "homemade": "health",
    "fast food": "health",
    "restaurant": "health",
    "delivery": "health",
    "friends": "social",
    "family": "social",
    "date": "social",
    "meditation": "better_me",
    "craft": "better_me",
    "kindness": "better_me",
    "listen": "better_me",
    "give gift": "better_me", #normalize?
    "gardening": "better_me",
    "pleasuread": "better_me",
    "nap": "better_me",
    "start early":"productivity",#normalize? 
    "make list":"productivity",#normalize?
    "focus":"productivity",
    "take a break":"productivity",#normalize?
    "shopping":"chores", 
    "cleaning":"chores", 
    "cooking":"chores", 
    "laundry":"chores", 
    "sunny":"weather",
    "clouds":"weather",
    "rain":"weather",
    "storm":"weather",
    "wind":"weather",
    "heat":"weather",
    "cold":"weather",
    "humid":"weather"
}

# Macro category per activity list (multi-label)
df["macro_activities"] = df["activities"].apply(lambda lst: sorted({mapping[a] for a in lst if a in mapping}))

# Check for any activities not covered by the mapping
all_activities = {item for sublist in df["activities"] for item in sublist}
unmapped = sorted(all_activities - mapping.keys())
print(f"Unmapped activities ({len(unmapped)}):", unmapped)

# Save cleaned dataset
df.to_csv("data/moods_cleaned.csv", index=False)

print("Cleaning complete. Cleaned file saved to data/moods_cleaned.csv")

# 3. Create the 8 new columns
activity_columns = ["emotions", "sleep", "health", "social", "better_me", "productivity", "chores", "weather"]

################################################# 
# Create the micro-activity binary columns for ML methods.

# Inspect unique values before binarization:
print(sorted({item for sublist in df["activities"] for item in sublist}))

mlb = MultiLabelBinarizer()
micro_df = pd.DataFrame(
    mlb.fit_transform(df["activities"]),
    columns=mlb.classes_,
    index=df.index
)

micro_df.columns = micro_df.columns.str.strip().str.lower()
micro_df = micro_df.T.groupby(level=0).max().T

print("micro_df created:", micro_df.shape)

micro_df.to_csv("data/moods_microacts.csv", index=False)

# Binarize macro categories the same way
mlb_macro = MultiLabelBinarizer()
macro_df = pd.DataFrame( mlb_macro.fit_transform(df["macro_activities"]),
                        columns=mlb_macro.classes_,
                        index=df.index
                       )

print("macro_df created:", macro_df.shape)

# Merge dfs: micro AND macro binary columns both join df
result_cross = df.merge(micro_df, left_index=True, right_index=True)
result_cross = result_cross.merge(macro_df, left_index=True, right_index=True)

#print(len(result_cross))

# Introduce macro_df:
# Drop the two list-form columns now that both are binarized —
# "activities" (micro) and "macro_activities" (macro) are redundant once expanded. 

macro_mood = result_cross.drop(columns=["activities", "macro_activities"])
print(macro_mood.head())

macro_mood.to_csv("data/moods_features.csv", index=False)

print("Multilabelled activities df saved as moods_features")

print(macro_mood.shape)
print(macro_mood.columns.value_counts())

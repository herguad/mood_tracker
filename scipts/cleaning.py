import pandas as pd
import numpy as np
import re
import ast
from sklearn.preprocessing import MultiLabelBinarizer


# Load raw data
df = pd.read_csv("data/raw_mood.csv")

print(df.columns)

# Standardize column names
df.columns = [c.strip().lower() for c in df.columns]

print(df.columns)

# Parse dates safely
df["full_date"] = pd.to_datetime(df["full_date"], errors="coerce")

# Drop rows with invalid or missing mood/date
df = df.dropna(subset=["full_date", "mood"])

# Normalize mood text (remove emojis, lowercase, strip)
def normalize_mood(m):
    m = m.lower().strip()
    m = re.sub(r"[^\w\s]", "", m)  # remove punctuation
    return m

df["mood"] = df["mood"].apply(normalize_mood)

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

############################################### Optional: clean intensity if present
if "intensity" in df.columns:
    df["intensity"] = pd.to_numeric(df["intensity"], errors="coerce").fillna(0).astype(int)

# Remove NaN columns and subdivide 'activities' into 8 categories: emotions,sleep, health, social, better me, productivity, chores and weather.

# 1. Drop unwanted columns
df = df.drop(columns=["date", "time", "scales", "note_title", "note"], errors="ignore")

# 2. Ensure 'activities' column contains actual lists
print(type(df.activities))

# Change | for commas in activities column to get lists instead of single strings.
df['activities']=df['activities'].str.split('|')
print(type(df.activities[5]))
print(df.activities[6])

# Ensure 'activities' column contains actual list with a parse_list() using 2 if loops isna, isinstance(x,str), 
# ast package, try/except ast.literal_eval(x), except return [i.strip() for i in x.split(",")]
#df["activities"] = df["activities"].apply(parse_list)


# Save cleaned dataset
df.to_csv("data/moods_cleaned.csv", index=False)

print("Cleaning complete. Cleaned file saved to data/moods_cleaned.csv")

# 3. Create the 8 new columns
activity_columns = ["emotions", "sleep", "health", "social", "better_me", "productivity", "chores", "weather"]

print(df["activities"].head())
print(type(df["activities"].iloc[0]))

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
    "excercise": "health",
    "drink water": "health",
    "walk": "health",
    "stretch": "health",
    "doctor": "health",
    "friends": "social",
    "family": "social",
    "date": "social",
    "meditation": "better_me",
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

################################################# 
# Create the micro-activity binary columns for ML methods.
#from sklearn.preprocessing import MultiLabelBinarizer
mlb = MultiLabelBinarizer()
micro_df = pd.DataFrame(
    mlb.fit_transform(df["activities"]),
    columns=mlb.classes_,
    index=df.index
)

micro_df.columns = micro_df.columns.str.strip().str.lower()

micro_df = micro_df.groupby(micro_df.columns, axis=1).max()


#micro_df.to_csv("data/moods_microacts.csv", index=False)

#print("Multilabelled activities df saved to data/moods_cleaned.csv")

print(micro_df.head())
print(micro_df.info())



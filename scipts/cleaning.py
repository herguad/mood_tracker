import pandas as pd
import re
import ast

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
df = df.drop(columns=["date", "time", "scales", "note_title", "note_title"], errors="ignore")

# 2. Ensure 'activities' column contains actual lists
print(type(df.activities))

# Change | for commas in activities column to get lists instead of single strings.
df['activities']=df['activities'].str.split('|')
print(type(df.activities[5]))


def parse_list(x):
    if pd.isna(x): 
        return []
    if isinstance(x, str):
        try:
            return ast.literal_eval(x)  # safer than eval()
        except:
            return [i.strip() for i in x.split(",")]  # fallback if stored as csv-like string
    return x

df["activities"] = df["activities"].apply(parse_list)

print(df.activities[6])

# 3. Create the 8 new columns
activity_columns = ["emotions", "sleep", "health", "social", "better_me", "productivity", "chores", "weather"]


# Save cleaned dataset
df.to_csv("data/moods_cleaned.csv", index=False)

print("Cleaning complete. Cleaned file saved to data/moods_cleaned.csv")
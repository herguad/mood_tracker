import sqlite3
import pandas as pd

# Connect to SQLite database (will create if it doesn't exist)
conn = sqlite3.connect("data/moods.db")

# Load cleaned data
df = pd.read_csv("data/moods_cleaned.csv")

# Drop derived / feature columns
df_db = df.drop(columns=["weekday", "activities"])

# Load into database
df_db.to_sql("moods", conn, if_exists="append", index=False)

conn.close()

print("Data successfully loaded into moods.db")

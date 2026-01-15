import pandas as pd
import matplotlib.pyplot as plt  

df = pd.read_csv("data/moods_features.csv")

df.info()
df.describe(include="all")

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

#Mood counts
barchart

#Activity frequency (SB)


#Heatmaps 
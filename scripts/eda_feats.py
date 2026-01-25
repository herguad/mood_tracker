import pandas as pd
import matplotlib.pyplot as plt  

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


#Activity frequency (SB)
#Which activities dominate the dataset?
print(df_feats.columns)

activities_cols= ['angry', 'anxious', 'bad sleep',
       'bored', 'cleaning', 'clouds', 'cold', 'content', 'cooking', 'date',
       'delivery', 'desperate', 'doctor', 'drink water', 'eat healthy',
       'excited', 'exercise', 'family', 'fast food', 'focus', 'friends',
       'gardening', 'give gift', 'good sleep', 'grateful', 'happy', 'heat',
       'homemade', 'humid', 'irritated', 'kindness', 'laundry', 'listen',
       'make list', 'meditation', 'medium sleep', 'nap', 'no meat',
       'pleasuread', 'rain', 'relaxed', 'restaurant', 'sad', 'shopping',
       'sleep early', 'start early', 'storm', 'stressed', 'stretch', 'sunny',
       'take a break', 'tired', 'unsure', 'walk', 'wind']


acts= df_feats.iloc[:,4:]

activity_counts = acts.sum().sort_values(ascending=False)

plt.figure(figsize=(10, 5))
plt.bar(activity_counts.index, activity_counts.values, color="green")

plt.title("Activity Frequency Across Mood Entries")
plt.xlabel("Activity")
plt.ylabel("Number of Entries")

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

#print("\nSums of activities columns: ")
#print(col_sums)
#Heatmaps 


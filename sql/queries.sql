-- Mood frequency overall
SELECT mood, COUNT(*) AS total
FROM moods
GROUP BY mood
ORDER BY total DESC;

-- Mood trend by month
SELECT strftime('%Y-%m', full_date) AS month, mood, COUNT(*) AS count
FROM moods
GROUP BY month, mood
ORDER BY month;

-- Mood transition (what mood tends to follow another)
SELECT 
    m1.mood AS mood_today,
    m2.mood AS mood_next_day,
    COUNT(*) AS transitions
FROM moods m1
JOIN moods m2
  ON date(m1.full_date, '+1 day') = m2.full_date
GROUP BY mood_today, mood_next_day
ORDER BY transitions DESC;

-- Mood counts per weekday
CREATE VIEW IF NOT EXISTS mood_weekday AS
SELECT 
    weekday,  -- 0 = Sunday ... 6 = Saturday
    mood,
    COUNT(*) AS mood_count
FROM moods
GROUP BY weekday, mood
ORDER BY weekday;
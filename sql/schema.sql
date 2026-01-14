-- 1. Main table
CREATE TABLE IF NOT EXISTS moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_date TEXT NOT NULL,       -- stored as ISO date (YYYY-MM-DD)
    mood TEXT NOT NULL,       -- categorical mood label
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 2. Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_moods_date ON moods(full_date);
CREATE INDEX IF NOT EXISTS idx_moods_mood ON moods(mood);

-- 3. A view for mood counts per weekday
CREATE VIEW IF NOT EXISTS mood_weekday AS
SELECT 
    strftime('%w', full_date) AS weekday,  -- 0 = Sunday ... 6 = Saturday
    mood,
    COUNT(*) AS mood_count
FROM moods
GROUP BY weekday, mood
ORDER BY weekday;


--- After loading cleaned CSV into SQLite or PostgreSQL: queries.sql
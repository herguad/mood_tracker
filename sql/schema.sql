CREATE TABLE IF NOT EXISTS moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_date TEXT NOT NULL,
    mood TEXT NOT NULL,
    intensity INTEGER,
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_moods_date ON moods(date);
CREATE INDEX IF NOT EXISTS idx_moods_mood ON moods(mood);

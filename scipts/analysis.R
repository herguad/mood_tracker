library(tidyverse)
library(lubridate)

df <- read_csv("data/moods_cleaned.csv")

df <- df %>%
  mutate(date = ymd(date),
         weekday = wday(date, label = TRUE))

# Mood frequency table
df %>% count(mood, sort = TRUE)

# Weekday mood counts
df %>% count(weekday, sort = TRUE)

# If intensity exists, compute monthly stats + 7-day rolling mean
if ("intensity" %in% colnames(df)) {
  df <- df %>%
    arrange(date) %>%
    mutate(rolling_mood = zoo::rollmean(intensity, 7, fill = NA, align = "right"))

  df %>% 
    mutate(month = floor_date(date, "month")) %>%
    group_by(month) %>%
    summarise(mean_intensity = mean(intensity, na.rm = TRUE),
              sd_intensity = sd(intensity, na.rm = TRUE),
              entries = n())
}

# Mood transitions (Markov-style, simplified)
df %>%
  arrange(date) %>%
  mutate(next_mood = lead(mood)) %>%
  count(mood, next_mood, sort = TRUE)

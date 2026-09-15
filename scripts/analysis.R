library(tidyverse)
library(lubridate)

df <- read_csv("data/moods_cleaned.csv")

df <- df %>%
  mutate(full_date = ymd(full_date),
         weekday = wday(full_date, label = TRUE))


# Mood transitions (Markov-style, simplified)
df %>%
  arrange(full_date) %>%
  mutate(next_mood = lead(mood)) %>%
  count(mood, next_mood, sort = TRUE)

library(tidyverse)
library(lubridate)

df <- read_csv("data/moods_cleaned.csv")

df <- df %>%
  mutate(full_date = ymd(full_date)) %>%
  arrange(full_date) %>%
  mutate(next_mood = lead(mood))

# Transition counts and conditional probabilities: P(next mood | current mood)
transition_counts <- df %>%
  filter(!is.na(next_mood)) %>%
  count(mood, next_mood)

transition_probs <- transition_counts %>%
  group_by(mood) %>%
  mutate(prob = n / sum(n)) %>%
  ungroup() %>%
  arrange(mood, desc(prob))

print(transition_probs, n = Inf)

# Full 5-category contingency table (for reference / inspection)
transition_table <- transition_counts %>%
  pivot_wider(names_from = next_mood, values_from = n, values_fill = 0)

print(transition_table)

# Collapse "awful" (n=3, too sparse to support on its own) into "bad" for testing
df_collapsed <- df %>%
  mutate(mood_collapsed = if_else(mood == "awful", "bad", mood),
         next_mood_collapsed = if_else(next_mood == "awful", "bad", next_mood))

transition_table_collapsed <- df_collapsed %>%
  filter(!is.na(next_mood_collapsed)) %>%
  count(mood_collapsed, next_mood_collapsed) %>%
  pivot_wider(names_from = next_mood_collapsed, values_from = n, values_fill = 0)

print(transition_table_collapsed)

chi_matrix <- transition_table_collapsed %>%
  column_to_rownames("mood_collapsed") %>%
  as.matrix()

# Chi-square test of independence — is next-day mood independent of current mood?
chi_result <- chisq.test(chi_matrix)
print(chi_result)

# Fisher's exact test (simulated) as a robustness check, given small expected
# cell counts flagged by the chi-square approximation warning above
fisher_result <- fisher.test(chi_matrix, simulate.p.value = TRUE, B = 10000)
print(fisher_result)

# Heatmap of transition probabilities (full 5-category, uncollapsed)
ggplot(transition_probs, aes(x = next_mood, y = mood, fill = prob)) +
  geom_tile() +
  geom_text(aes(label = scales::percent(prob, accuracy = 1)), color = "white", size = 3) +
  scale_fill_viridis_c(name = "P(next mood)") +
  labs(title = "Mood Transition Probabilities", x = "Next Mood", y = "Current Mood") +
  theme_minimal()

ggsave("outputs/mood_transition_heatmap.png", width = 8, height = 6, dpi = 150)

# ---- Association strength: Cramer's V between mood and individual activities ----
# Restricted to behavioral/weather/macro columns; emotion tags excluded since they
# are a granular echo of the mood field itself and dominate any joint ranking
# with mood, obscuring genuinely behavioral associations.

library(rcompanion)

macro_cols <- c("emotions", "sleep", "health", "social", "better_me", "productivity", "chores", "weather")
weather_micro <- c("sunny", "clouds", "rain", "storm", "wind", "heat", "humid", "cold")
emotion_micro <- c("happy", "excited", "grateful", "relaxed", "content", "tired", "unsure",
                    "bored", "anxious", "angry", "stressed", "sad", "desperate", "irritated")

all_micro_cols <- setdiff(names(df), c(macro_cols, "mood", "full_date", "period", "weekday"))
behavioral_micro <- setdiff(all_micro_cols, c(weather_micro, emotion_micro))
non_emotion_cols <- c(behavioral_micro, weather_micro, macro_cols)

cramers_results_behavioral <- map_dfr(non_emotion_cols, function(col) {
  tbl <- table(df$mood, df[[col]])
  v <- tryCatch(cramerV(tbl), error = function(e) NA)
  tibble(activity = col, cramers_v = v)
})

activity_freq <- df %>%
  summarise(across(all_of(non_emotion_cols), ~ mean(.x))) %>%
  pivot_longer(everything(), names_to = "activity", values_to = "freq")

# Flag associations backed by too few observations (<5% of entries) as unreliable,
# rather than silently dropping them — mirrors the small-n handling used
# throughout the rest of this project (e.g. the "awful" mood category)
cramers_results_behavioral <- cramers_results_behavioral %>%
  left_join(activity_freq, by = "activity") %>%
  mutate(reliable = freq >= 0.05) %>%
  arrange(desc(cramers_v))

print(cramers_results_behavioral, n = Inf)

# ---- Ordinal logistic regression: mood ~ macro activities + period ----
# Predictors restricted to macro categories (excluding near-universal
# sleep/weather/emotions, which showed minimal variance to associate with
# mood in the Cramer's V analysis above) plus period.

library(MASS)  # NOTE: MASS::select() masks dplyr::select() — use dplyr::select()
               # explicitly if needed elsewhere in this session

df <- df %>%
  mutate(mood = factor(mood, levels = c("awful", "bad", "meh", "good", "rad"), ordered = TRUE))

# Lagged mood predictor, to account for the day-to-day mood autocorrelation
# already established by the transition/chi-square tests earlier in this script —
# without this, standard errors on the activity predictors would be overconfident.
df_lagged <- df %>%
  arrange(full_date) %>%
  mutate(mood_lag1 = lag(mood)) %>%
  filter(!is.na(mood_lag1))

# Baseline model (no lag), fit on the same rows as the lagged model for a
# valid likelihood ratio comparison
mood_model <- polr(
  mood ~ health + social + better_me + productivity + chores + period,
  data = df_lagged,
  Hess = TRUE
)

mood_model_lag <- polr(
  mood ~ health + social + better_me + productivity + chores + period + mood_lag1,
  data = df_lagged,
  Hess = TRUE
)

# p-values (polr reports t-values only; compute via normal approximation)
get_polr_pvalues <- function(model) {
  coefs <- coef(summary(model))
  p_values <- pnorm(abs(coefs[, "t value"]), lower.tail = FALSE) * 2
  cbind(coefs, "p value" = p_values)
}

print(get_polr_pvalues(mood_model))
print(get_polr_pvalues(mood_model_lag))

# Confirm the lagged model is a significant improvement over the baseline
anova(mood_model, mood_model_lag)
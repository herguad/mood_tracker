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

ggsave("imgs/mood_transition_heatmap.png", width = 8, height = 6, dpi = 150)
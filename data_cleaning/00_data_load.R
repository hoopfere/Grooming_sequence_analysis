library(tidyverse)
library(here)
library(readxl)
library(janitor)

heat_25_df <- readxl::read_xlsx(here("data","HeatExpt_25C.xlsx")) %>% 
  clean_names()
head_37_df <- readxl::read_xlsx(here("data","HeatExpt_37C.xlsx")) %>% 
  clean_names()



heat_25_specific <- heat_25_df %>% 
  filter(behavior != "class_all_grooming") %>% 
  mutate(end_time = start_time + duration) 

heat_37_specific <- head_37_df %>% 
  filter(behavior != "class_all_grooming") %>% 
  mutate(end_time = start_time + duration) 

# Data Inconsistency Identification ----

## 37 Degree Exposure ----
heat_37_specific %>%
  arrange(file, start_time) %>%
  group_by(file) %>%
  filter(start_time < lag(end_time) - 1e-6) 

heat_37_inconsistencies <- c("240327Heat2_2024_03_27T20_10_17_497Z_CH3_MM_updated.xlsx", 
                             "AS240212_GR_H_UASmales1_2024_02_12T20_39_15_920Z_CH3_updated.xlsx",    
                             "AS240212_GR_H_UASmales1_2024_02_12T20_39_15_920Z_CH4_MRC_updated.xlsx",
                             "EH250923_HEAT_1_37_Degrees_2025_09_23T21_30_47_503Z_CH5_MM.xlsx")

heat_37_specific %>% 
  filter(file %in% heat_37_inconsistencies[1]) %>% View()

# 25 Degree Exposure ----
heat_25_specific %>%
  arrange(file, start_time) %>%
  group_by(file) %>%
  filter(start_time < lag(end_time) - 1e-6)

heat_25_inconsistencies <- c("240327Heat2_2024_03_27T20_10_17_497Z_CH6_AH_updated.xlsx",
                             "JP240131_GR_H_UASmales1_2024_01_31T22_50_55_867Z_CH7_CL_updated.xlsx")

heat_25_specific %>% 
  filter(file %in% heat_25_inconsistencies[1]) %>% View() # Check for CH6_AH start 240 and CH7_CL start 5.87

# Fill Neutral Gaps ----
fill_neutral_gaps <- function(df,
                              total_start = 0,
                              total_end = 300,
                              all_ids = unique(df$file)) {
  
  safety <- 1e-6 
  neutral_list <- list()
  
  for (id in all_ids) {
    # Filters for each individual fly and arranges the start time
    sub <- df %>%
      filter(file == id) %>%
      arrange(start_time)
    
    current_time <- total_start # This starts at default 0.00 seconds, will update as we traverse
    gaps <- tibble()
    
    # Goes through each row of each individual
    for (j in seq_len(nrow(sub))) {
      
      # Identifies if there is a gap between what looked at and the next entry's start time
      if (sub$start_time[j] > current_time + safety) {
        gaps <- gaps %>%
          bind_rows(tibble(file = id,
                           behavior = "neutral",
                           start_time = current_time,
                           end_time = sub$start_time[j]))
      }
      
      # Updates the current time traversal (Is max needed? Check inconsistencies)
      current_time <- max(current_time, sub$end_time[j])
    }
    
    # Last gap from last grooming action to end of trail period
    if (current_time < total_end - safety) {
      gaps <- gaps %>%
        bind_rows(tibble(file = id,
                         behavior = "neutral",
                         start_time = current_time,
                         end_time = total_end))
    }
    
    neutral_list[[length(neutral_list) + 1]] <- gaps
  }
  
  df_full <- df %>%
    bind_rows(bind_rows(neutral_list)) %>%
    arrange(file, start_time)
  
  df_full
}

heat_25_filled <- fill_neutral_gaps(heat_25_specific) %>% 
  mutate(duration = if_else(is.na(duration), end_time - start_time, duration),
         genotype = "control_5min")

heat_37_filled <- fill_neutral_gaps(heat_37_specific) %>% 
  mutate(duration = if_else(is.na(duration), end_time - start_time, duration),
         genotype = "heat_5min") 

saveRDS(heat_25_filled,here("processed_data","heat_25_filled.RDS"))
saveRDS(heat_37_filled,here("processed_data","heat_37_filled.RDS"))

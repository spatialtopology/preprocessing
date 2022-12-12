library(tidyverse)

extract_bids <- function(d, column){
  d |> 
    mutate(
      modality = if_else(str_detect({{column}}, "T1w"), "T1w", "bold"),
      sub = str_extract({{column}}, "(?<=sub-)[[:digit:]]+"),
      ses = str_extract({{column}}, "(?<=ses-)[[:digit:]]+"),
      task = str_extract({{column}}, "(?<=task-)[[:alpha:]]+"),
      run = str_extract({{column}}, "(?<=run-)[[:digit:]]+"))
}

full <- read_delim("params0", delim = "\n", col_names = "nii") |> 
  filter(str_detect(nii, "dup", negate = TRUE)) |>
  mutate(
    modality = if_else(str_detect(nii, "T1w"), "T1w", "bold"),
    json = str_replace(nii, "nii.gz", "json")) |>
  extract_bids(nii) |>
  select(nii, json, sub, ses, modality, task, run)

# write initial list of params for determining what to run
full |> 
  write_delim("params", col_names = FALSE)

# -------------

# find which new participants have yet to be run
done <- read_delim("jsons", delim = "\n", col_names = "out") |> 
  mutate(modality = if_else(str_detect(out, "T1w"), "T1w", "bold")) |>
  extract_bids(out) 

# find new list of subs to run
anti_join(full, done) |>
  write_delim("params", col_names = FALSE)

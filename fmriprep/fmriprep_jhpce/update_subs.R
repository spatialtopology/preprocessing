library(tidyverse)


subs <- read_delim("subs", delim = "\n", col_names = "sub") |>
  mutate(row = 1:n())

done <- read_delim("done-av", delim = "\n", col_names = "row") 

# find new list of subs to run
anti_join(subs, done) 

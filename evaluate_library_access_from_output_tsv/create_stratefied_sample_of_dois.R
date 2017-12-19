# Load dependencies ------------------------------------------------------------

# Load magrittr pipe
`%>%` = dplyr::`%>%`

# Settings ---------------------------------------------------------------------

lzma_compressed_library_access_data_location <- file.path(
  'data', 'library_coverage_xml_and_fulltext_indicators.tsv.xz'
)

sample_size_per_cell <- 100  # This will be for each cell, multiplied by 
# 2 full_text_indicator status

output_tsv_location <- file.path(
  'evaluate_library_access_from_output_tsv',
  'manual-doi-checks.tsv'
)

randomizer_seed_to_set <- 3  # Ensure that random sampling will always return
# the same result.

# Read the dataset -------------------------------------------------------------

library_access_data <- read.table(
  gzfile(lzma_compressed_library_access_data_location),
  sep = '\t',
  header = TRUE
)
# View(lzma_compressed_library_access_data)  # Check the dataset

# Convert variable to factor:
library_access_data <- library_access_data %>% dplyr::mutate(
  full_text_indicator = as.factor(full_text_indicator)
)

# Create stratefied sample, and clean up the tibble ----------------------------

set.seed(randomizer_seed_to_set)
stratefied_sample <- library_access_data %>%
  dplyr::group_by(full_text_indicator) %>%
  dplyr::sample_n(sample_size_per_cell) %>%
  # Add columns to fill in manually to the stratefied sample dataframe:
  dplyr::rename('full_text_indicator_automated' = 'full_text_indicator') %>%
  dplyr::mutate(
    date_of_manual_full_text_check = NA,
    full_text_indicator_manual = NA
  )

# Write the output to a TSV ----------------------------------------------------

readr::write_tsv(
  stratefied_sample,
  output_tsv_location,
  na = ''
)

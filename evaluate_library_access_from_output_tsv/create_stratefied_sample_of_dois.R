#### Load libraries ####

library('dplyr')

#### Settings ####

lzma_compressed_library_access_tsv_location <- file.path(
  'data', 'library_coverage_xml_and_fulltext_indicators.tsv.xz'
)

original_dataset_with_oa_color_column_location <- paste0(
  'https://github.com/greenelab/scihub/raw/',
  '4172526ac7433357b31790578ad6f59948b6db26/data/',
  'state-of-oa-dois.tsv.xz'
)

sample_size_per_cell <- 20  # This will be for each cell, multiplied by 
# 2 full_text_indicator status * 5 OA "colors"

output_tsv_location <- file.path(
  'evaluate_library_access_from_output_tsv',
  'stratefied_sample_of_dois_and_manual_full_text_check_results.tsv'
)

randomizer_seed_to_set <- 3  # Ensure that random sampling will always return the same result.

#### Read and merge datasets ####

source(file.path(
  'evaluate_library_access_from_output_tsv',
  'read_and_merge_library_access_datasets.R'
))

# The function below will return a merged dataset, but will *also* add the
# following datasets to our global environment:
  # original_dataset_with_oa_color_column
  # lzma_compressed_library_access_tsv

merged_datasets <- read_and_merge_library_access_datasets(
  lzma_compressed_library_access_tsv_location,
  original_dataset_with_oa_color_column_location
)

# Convert variables to factors:
merged_datasets$oadoi_color <- factor(merged_datasets$oadoi_color)
merged_datasets$full_text_indicator <- factor(
  merged_datasets$full_text_indicator
)

#### Create stratefied sample within full_text_access and oadoi_color ####

set.seed(randomizer_seed_to_set)
stratefied_sample <- merged_datasets %>%
  group_by(full_text_indicator, oadoi_color) %>%
  sample_n(sample_size_per_cell)

#### Add columns to fill in manually to the stratefied sample dataframe ####

colnames(stratefied_sample)[3] <- 'full_text_indicator_automated'

stratefied_sample$date_of_manual_full_text_check <- NA
stratefied_sample$full_text_indicator_manual <- NA

#### Write the output to a TSV ####

write.table(
  stratefied_sample,
  file = output_tsv_location,
  sep = '\t',
  na = '',
  row.names = FALSE
)

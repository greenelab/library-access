# Settings ----------------------------------------------------------------

doi_200_dataset_location <- file.path(
  "evaluate_library_access_from_output_tsv",
  "manual-doi-checks.tsv"
)

doi_500_dataset_location <- file.path(
  "evaluate_library_access_from_output_tsv",
  "manual-doi-checks-500.tsv"
)

output_tsv_location <- file.path(
  'evaluate_library_access_from_output_tsv',
  'manual-doi-checks-500.tsv'
)

# Read data ---------------------------------------------------------------

# Load magrittr pipe
`%>%` = dplyr::`%>%`

doi_200_data <- readr::read_tsv(
  file = doi_200_dataset_location,
  col_types = "cccccc"  # Just read everything as a character.
)
# View(doi_200_data)  # Check our work

doi_500_data <- readr::read_tsv(
  file = doi_500_dataset_location,
  col_types = "cccccc"  # Just read everything as a character.
)
# View(doi_500_data)  # Check our work

# Apply dates from 200 dataset to 500 dataset -----------------------------

doi_500_data_imputed <- doi_500_data %>%
  dplyr::left_join(doi_200_data, by = "doi") %>%
  dplyr::mutate(
    penn_access_date = ifelse(
      is.na(penn_access_date),
      date_of_manual_full_text_check_inside_campus,
      penn_access_date
    ),
    open_access_date = ifelse(
      is.na(open_access_date),
      date_of_manual_full_text_check_outside_campus,
      open_access_date
    )
  ) %>%
  dplyr::select(colnames(doi_500_data))

readr::write_tsv(
  doi_500_data_imputed,
  output_tsv_location,
  na = ''
)
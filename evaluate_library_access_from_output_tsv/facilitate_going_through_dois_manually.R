#### Settings ####

manual_tsv_location <- file.path(
  'evaluate_library_access_from_output_tsv',
  'manual-doi-checks.tsv'
)

#### Open the tsv ####

dataset_to_go_through <- read.table(
  manual_tsv_location,
  sep = '\t',
  na.strings = '',
  header = TRUE,
  colClasses = 'character'
)
# View(dataset_to_go_through)

#### Facilitate going through the rows that haven't been filled in ####

for (row_number in 
  which(
    is.na(dataset_to_go_through$full_text_indicator_manual)
  )
) {
  doi_for_row <- dataset_to_go_through$doi[row_number]
  
  url_to_visit <- paste0(
    'https://doi.org/',
    doi_for_row
  )
  
  message('Opening URL "', url_to_visit, '"...')
  
  utils::browseURL(url_to_visit)
  
  while (TRUE) {
    user_full_text_input <- readline(
      'Do we have full-text access to this DOI? [y/n/invalid]
  ("invalid" = invalid DOI)'
    )
    
    if (
      tolower(user_full_text_input) == 'y' ||
      tolower(user_full_text_input) == 'n' ||
      tolower(user_full_text_input) == 'invalid'
    ) {
      dataset_to_go_through$date_of_manual_full_text_check[
        row_number
      ] <- as.character(Sys.Date())
      
      if (tolower(user_full_text_input) == 'y') {
        dataset_to_go_through$full_text_indicator_manual[row_number] <- 1
      } else if (tolower(user_full_text_input) == 'n') {
        dataset_to_go_through$full_text_indicator_manual[row_number] <- 0
      } else {
        dataset_to_go_through$full_text_indicator_manual[row_number] <- 'invalid'
      }
      
      break  # Break out of the loop, and move on.
    } else {
      message('Please enter y, n, or invalid. Asking again...')
    }
  }
  
  # Save the changes to the tsv:
  write.table(
    dataset_to_go_through,
    file = manual_tsv_location,
    sep = '\t',
    na = '',
    row.names = FALSE
  )
}

#### Read the datasets ####

read_and_merge_library_access_datasets <- function(
  lzma_compressed_library_access_tsv_location,
  original_dataset_with_oa_color_column_location
){
  # '<<-' at several places below will add the variable into our global scope,
  # beyond this function.
  lzma_compressed_library_access_tsv <<- read.table(
    gzfile(lzma_compressed_library_access_tsv_location),
    sep = '\t',
    header = TRUE
  )
  # View(lzma_compressed_library_access_tsv)  # Check the dataset
  
  # Create a temporary filepath for downloading the original dataset.
  # Then download and read it.
  tmp_filpath_for_original_dataset <- tempfile()
  
  download.file(
    original_dataset_with_oa_color_column_location,
    destfile = tmp_filpath_for_original_dataset,
    mode = 'wb'
  )
  
  original_dataset_with_oa_color_column <<- read.table(
    gzfile(tmp_filpath_for_original_dataset),
    sep = '\t',
    header = TRUE
  )
  # View(original_dataset_with_oa_color_column)  # Check the dataset
  
  #### Merge the datasets ####
  
  # Combine the datasets so that we have doi, full_text_indicator,
  # and oadoi_color
  merged_datasets <- merge(
    original_dataset_with_oa_color_column,
    lzma_compressed_library_access_tsv,
    by = "doi"
  )
  # View(merged_datasets)  # Check our work
  
  return(merged_datasets)
}
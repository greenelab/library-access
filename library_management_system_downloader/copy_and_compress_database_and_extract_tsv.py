# =============================================================================
# Import libraries
# =============================================================================

import logging
import lzma
import pandas as pd
from pathlib import Path
import shutil
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

# =============================================================================
# Settings
# =============================================================================

sqlite_database_location = 'library_coverage_xml_and_fulltext_indicators.db'

data_directory = 'data'

compressed_database_copy_name = (
        'library_coverage_xml_and_fulltext_indicators'
        '.db.xz')

tsv_output_file_name = 'library_coverage_xml_and_fulltext_indicators.tsv.xz'

# =============================================================================
# Create additional settings
# =============================================================================

logging.basicConfig(level=logging.INFO)

# =============================================================================
# Set up a connection to (and tables within) the SQLite database:
# =============================================================================

# Initialize the database:
Base = automap_base()
sql_engine = create_engine(f'sqlite:///{sqlite_database_location}')
Base.prepare(sql_engine, reflect=True)

dois_table = Base.classes.dois_table
library_holdings_data = Base.classes.library_holdings_data

# From the sqlalchemy documentation
# (http://docs.sqlalchemy.org/en/latest/orm/session_basics.html)
# Create a configured "session":
Session = sessionmaker(bind=sql_engine)
sql_session = Session()

# =============================================================================
# Create the data directory if it doesn't already exist
# =============================================================================

Path(data_directory).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Extract data from the databse, and save that as a TSV
# =============================================================================

# We'll first define a subquery to get just the latest full text information
# for each DOI:
dataset_max_timestamp_for_each_doi_query = sql_session.query(
        func.max(library_holdings_data.primary_key)).group_by(
                library_holdings_data.doi_foreign_key)

# str(dataset_max_timestamp_for_each_doi_query)  # See the SQL being used.
# list(dataset_max_timestamp_for_each_doi_query)  # See the list of max
# primary keys.

# We'll now get the DOI and full-text indicator based on the subquery above:
dataset_join_query = sql_session.query(
        dois_table.doi,
        # library_holdings_data.timestamp,  # Uncomment to also get the
        # timestamp of the DOI fulltext query
        # library_holdings_data.xml_response,  # Uncomment to also get the
        # full XML response.
        library_holdings_data.full_text_indicator) \
        .join(library_holdings_data) \
        .group_by(dois_table.doi) \
        .filter(library_holdings_data.primary_key.in_(
                dataset_max_timestamp_for_each_doi_query))

joined_dataset = pd.read_sql(
            dataset_join_query.statement,
            dataset_join_query.session.bind)

# Sort the dataset by DOI and timestamp, so that it will always be in the
# same order:
joined_dataset.sort_values(
        by=["doi"],
        inplace=True)

tsv_output_path = str(Path(data_directory, tsv_output_file_name))

logging.info(
        f'Creating a TSV from the database, at "{tsv_output_path}"...')

joined_dataset.to_csv(
        path_or_buf=tsv_output_path,
        sep='\t',
        index=False,  # Do not write row numbers
        compression='xz')

# =============================================================================
# Save a compressed copy of the database
# =============================================================================


def xz_compress_a_file(
        input_file_location,
        output_file_location):
    """Compress an existing file with lzma compression.

    This follows an example from the gzip documentation, at
    https://docs.python.org/3/library/gzip.html, and applies the same logic
    using lzma."""

    with open(input_file_location, f'rb') as \
        input_file, \
        lzma.open(output_file_location, 'wb') as \
            output_file:
            shutil.copyfileobj(input_file, output_file)


database_output_path = str(Path(
        data_directory, compressed_database_copy_name))

logging.info(
        f'Creating a copy of the database under "'
        f'{database_output_path}"...')

xz_compress_a_file(sqlite_database_location, database_output_path)

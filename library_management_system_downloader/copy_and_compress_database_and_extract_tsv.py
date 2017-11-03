# =============================================================================
# Import libraries
# =============================================================================

import logging
import lzma
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

# =============================================================================
# Settings
# =============================================================================

sqlite_database_location = 'library_coverage_xml_and_fulltext_indicators.db'

data_directory = 'data'

compressed_database_copy_name = (
        'library_coverage_xml_and_fulltext_indicators'
        '.db.xz')

tsv_output_file_name = 'library_coverage_xml_and_fulltext_indicators.tsv'

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

if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# =============================================================================
# Extract data from the databse, and save that as a TSV
# =============================================================================

dataset_join_query = sql_session.query(
        dois_table.doi,
        library_holdings_data.timestamp,
        # library_holdings_data.xml_response,
        library_holdings_data.full_text_indicator).join(library_holdings_data)

joined_dataset = pd.read_sql(
            dataset_join_query.statement,
            dataset_join_query.session.bind)

# Sort the dataset by DOI and timestamp, so that it will always be in the
# same order:
joined_dataset.sort_values(
        by=["timestamp", "doi"],
        inplace=True)

tsv_output_path = os.path.join(data_directory, tsv_output_file_name)

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

database_output_path = os.path.join(
        data_directory, compressed_database_copy_name)

logging.info(
        f'Creating a copy of the database under "'
        f'{database_output_path}"...')

with open(sqlite_database_location, "rb") as database_file:
    with lzma.open(database_output_path, "wb") as output_file:
        output_file.writelines(database_file)

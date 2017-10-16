import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import Table, MetaData, Column, String, DateTime, Integer, func
from sqlalchemy import ForeignKey, distinct
from sqlalchemy.orm import sessionmaker

# =============================================================================
# Load configuration variables
# =============================================================================

# Location of configuration file.
# This should be a python script (named with a .py file extension), and
# should contain  variables named the following:
# - static_parameters_for_api (a dictionary)
# - user_agent_custom_string (a string)
# - api_base_url (a string)
# -tsv_dataset_location (a filepath string)

from library_management_system_downloader \
        import downloader_configuration_file as config
# config.api_base_url
# config.user_agent_custom_string
# config.static_parameters_for_api
# config.tsv_dataset_location

from library_management_system_downloader import create_api_request as api
from library_management_system_downloader \
        import evaluate_api_response_for_fulltext_indication as fulltext

# =============================================================================
# Create additional settings
# =============================================================================

logging.basicConfig(level=logging.INFO)

# =============================================================================
# Set up a connection to (and tables within) an SQLite database:
# =============================================================================

# Initialize the database:
sql_engine = create_engine(
        'sqlite:///library_coverage_xml_and_fulltext_indicators.db')


# From the sqlalchemy documentation, at
# http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html:
# Turn on write-ahead logging, which will allow reading and writing at
# the same time (without this, I was getting an error re: the database being
# locked when chunksize is used with read_sql_query, since that returns a
# generator and is thus still reading the database:
@event.listens_for(sql_engine, "connect")
def set_sqlite_pragma(sql_engine, connection_record):
    cursor = sql_engine.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

# Create an sqlalchemy metadata schema:
metadata = MetaData(sql_engine)

# Create a schema for the table that will hold the API data:
# The full_text_indicator column will be an integer in that 1 = fulltext
# available and 0 = fulltext not available:
dois_table = Table(
        'dois_table', metadata,
        Column('database_id', Integer, primary_key=True),
        Column('doi', String, nullable=False, unique=True, index=True))

library_holdings_table = Table(
        'library_holdings_data', metadata,
        Column('doi_foreign_key',
               String, ForeignKey("dois_table.database_id"), nullable=False),
        Column('timestamp', DateTime, nullable=False,
               default=func.now()),  # Default is creation time
        Column('xml_response', String, nullable=False),
        Column('full_text_indicator', Integer))

dois_table.create(
        checkfirst=True)  # Don't create the table if it already exists.

library_holdings_table.create(
        checkfirst=True)  # Don't create the table if it already exists.

# Create an sqlalchemy portal for inserting new records into
# the tables:
dois_table_insert = dois_table.insert()
holdings_table_insert = library_holdings_table.insert()

# =============================================================================
# Define functions for querying and inserting into the database
# =============================================================================

Session = sessionmaker(bind=sql_engine)
sql_session = Session()


def is_doi_already_answered_in_database(
        doi,
        sqlalchemy_session=sql_session):
    existing_doi_with_fulltext_anwer = sql_session.query(distinct(
        dois_table.c.doi)).join(library_holdings_table).filter(
            dois_table.c.doi == doi).filter(
                    library_holdings_table.c.full_text_indicator.isnot(
                            None)).first()

    if existing_doi_with_fulltext_anwer is None:
        return False
    else:
        return True

# Example invocation:
# is_doi_already_answered_in_database('10.1001/2012.jama.10139')


def insert_a_doi_database_record(
        doi,
        api_response_text,
        full_text_indicator_for_doi,
        sqlalchemy_session=sql_session):
    doi_foreign_key = sql_session.query(
            distinct(dois_table.c.database_id)).filter(
                    dois_table.c.doi == doi).first()

    if doi_foreign_key is None:
        logging.info('Inserting DOI "%s" into the database...' % doi)
        inserted_doi = dois_table_insert.execute(doi=doi)
        # Get the foreign key we just inserted into the database:
        doi_foreign_key = inserted_doi.inserted_primary_key[0]
    else:
        doi_foreign_key = doi_foreign_key[0]
        logging.info('DOI "%s" is already in the database (foreign key "%i"), '
              'so not inserting it...'
              % (doi, doi_foreign_key))

    # Insert the new XML record:
    logging.info('Inserting holdings record into database...')
    holdings_table_insert.execute(
            doi_foreign_key=doi_foreign_key,
            xml_response=api_response_text,
            full_text_indicator=full_text_indicator_for_doi)

# =============================================================================
# Import the list of DOIs
# =============================================================================

# Import the datset into
doi_dataset = pd.read_csv(config.tsv_dataset_location, sep='\t', header=0)

# Set will get unique values in the list:
list_of_dois = list(set(
        doi_dataset[doi_dataset['oadoi_color'] == 'closed']['doi']))
# len(list_of_dois)

# Note that we will use config.rerun_dois_that_are_already_in_database to
# determine below whether to re-run DOIs that already have an answer in the
# database.

# =============================================================================
# Query the API
# =============================================================================

for doi in list_of_dois[0:2]:
    if (config.rerun_dois_that_are_already_in_database is not True and
            is_doi_already_answered_in_database(doi) is True):
            logging.info(
                    'DOI is already in the database with a fulltext answer. '
                    'config.rerun_dois_that_are_already_in_database is not '
                    'True. Therefore, moving on to the next DOI...')
    else:
        # I'm leaving this here as an example to make manual debugging
        # easier:
        # doi = '10.1001/2012.jama.10139'

        api_response = api.create_api_request(
                doi,
                api_base_url=config.api_base_url,
                static_api_request_parameters_dictionary=config.
                static_parameters_for_api,
                custom_user_agent_string=config.user_agent_custom_string)

        # Demonstrating how to interact with the api_response:
        # api_response.url
        # api_response.status_code
        # api_response.text

        full_text_indicator_for_doi = \
            fulltext.fulltext_indication(api_response.text)

        # =====================================================================
        # Insert a record into the SQLite table
        # =====================================================================

        insert_a_doi_database_record(doi, api_response.text,
                                     full_text_indicator_for_doi)

        # An example of re-joining the two tables:
        # sql_session.query(
        #         dois_table.c.doi,
        #         library_holdings_table.c.timestamp,
        #         library_holdings_table.c.full_text_indicator).join(
        #                 library_holdings_table).all()

import logging
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import Table, MetaData, Column, String, DateTime, Integer, func

# =============================================================================
# Load configuration variables
# =============================================================================

# Location of configuration file.
# This should be a python script (named with a .py file extension), and
# should contain  variables named the following:
# - static_parameters_for_api (a dictionary)
# - user_agent_custom_string (a string)
# - api_base_url (a string)

from library_management_system_downloader \
        import downloader_configuration_file as config
# config.api_base_url
# config.user_agent_custom_string
# config.static_parameters_for_api

from library_management_system_downloader import create_api_request as api
from library_management_system_downloader \
        import evaluate_api_response_for_fulltext_indication as fulltext

# =============================================================================
# Create additional settings
# =============================================================================

logging.basicConfig(level=logging.INFO)

#  TODO: Because iPython in Spyder seems to have a bug whereby logging.info()
# is not output, even with basicConfig set below, I've used print() below
# instead of logging.info for now. Changing this is a TODO item.

# =============================================================================
# Set up a connection to (and table within) an SQLite database:
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
library_holdings_table = Table(
        'library_holdings_data', metadata,
        Column('doi', String, primary_key=True),
        Column('timestamp', DateTime, nullable=False,
               default=func.now()),  # Default is creation time
        Column('xml_response', String, nullable=False),
        Column('full_text_indicator', Integer))

library_holdings_table.create(
        checkfirst=True)  # Don't create the table if it already exists.

# Create an sqlalchemy portal for inserting new records into
# library_holdings_table:
holdings_table_insert = library_holdings_table.insert()

# =============================================================================
# Query the API
# =============================================================================

doi = '10.1001/2012.jama.10139'

test_response = api.create_api_request(
        doi,
        api_base_url=config.api_base_url,
        static_api_request_parameters_dictionary=config.
        static_parameters_for_api,
        custom_user_agent_string=config.user_agent_custom_string)

# Demonstrating how to interact with the test_response:
# test_response.url
# test_response.status_code
# test_response.text

full_text_indicator_for_doi = \
    fulltext.fulltext_indication(test_response.text)

# =============================================================================
# Insert a record into the SQLite table
# =============================================================================

holdings_table_insert.execute(
        doi=doi,
        xml_response=test_response.text,
        full_text_indicator=full_text_indicator_for_doi)

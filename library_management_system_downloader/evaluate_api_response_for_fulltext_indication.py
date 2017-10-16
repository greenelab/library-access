from bs4 import BeautifulSoup
import logging


def fulltext_indication(api_response_xml):
    """Given XML from an API response, determine whether fulltext is available
    for that item. Return True if fulltext is available, and False if it is
    not."""
    parseable_response_xml = BeautifulSoup(
            api_response_xml,
            features='xml')

    doi_value = parseable_response_xml.find(
            id='rft.doi').string

    full_text_indicator_value = parseable_response_xml.find(
            id='full_text_indicator')

    logging.info(
          f'The value for the "full_text_indicator" key for doi "{doi_value}" '
          'is "full_text_indicator_value".')

    if(full_text_indicator_value is not None and
       full_text_indicator_value.string == 'true'):
        return 1
    else:
        return 0

# =============================================================================
# Function examples
# =============================================================================

# Should always return 1:
# evaluate_api_response_for_fulltext_indication(
#         '<key id="full_text_indicator">true</key>')

# Should always return 0:
# evaluate_api_response_for_fulltext_indication('tester')

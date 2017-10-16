from bs4 import BeautifulSoup
import logging

#  TODO: Because iPython in Spyder seems to have a bug whereby logging.info()
# is not output, even with basicConfig set below, I've used print() below
# instead of logging.info for now. Changing this is a TODO item.


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

    print(
          'The value for the "full_text_indicator" key for doi "%(doi)s" is '
          '"%(value)s".' % {
                  'doi': doi_value,
                  'value': full_text_indicator_value})

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

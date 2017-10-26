from bs4 import BeautifulSoup
import logging
import unittest


def fulltext_indication(api_response_xml):
    """Given XML from an API response, determine whether fulltext is available
    for that item. Return True if fulltext is available, and False if it is
    not."""
    parseable_response_xml = BeautifulSoup(
            api_response_xml,
            features='xml')

    doi_value = parseable_response_xml.find(
            id='rft.doi')

    full_text_indicator_value = parseable_response_xml.find(
            id='full_text_indicator')

    logging.info(
          f'The value for the "full_text_indicator" key for doi "{doi_value}" '
          'is "full_text_indicator_value".')

    if full_text_indicator_value is None:
        return 0
    return int(full_text_indicator_value.string == 'true')  # This will
    # evaluate to either 1 or 0.

# =============================================================================
# Function examples / tests
# =============================================================================


class TestFulltextIndication(unittest.TestCase):

    def test_true(self):
        self.assertEqual(
                fulltext_indication(
                        '<key id="full_text_indicator">true</key>'),
                1)

    def test_false(self):
        self.assertEqual(
                fulltext_indication('tester'),
                0)

# unittest.main()  # To run the above unit tests.

import pytest

import evaluate_api_response_for_fulltext_indication as to_test


@pytest.mark.parametrize(['xml', 'fulltext'], [
    ('<key id="full_text_indicator">true</key>', 1),
    ('<wrapper><key id="full_text_indicator">true</key></wrapper>', 1),
    ('<key id="full_text_indicator">false</key>', 0),
    ('tester', 0),
    ('', 0),
])
def test_fulltext_indication(xml, fulltext):
    assert to_test.fulltext_indication(xml) == fulltext

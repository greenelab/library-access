import evaluate_api_response_for_fulltext_indication as to_test


def test_fulltext_indication():
    assert to_test.fulltext_indication(
            '<key id="full_text_indicator">true</key>') == 1

    assert to_test.fulltext_indication('tester') == 0

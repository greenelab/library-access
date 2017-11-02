import logging

import backoff
from ratelimit import rate_limited
import requests


class ErrorWithAPI(Exception):
    pass


# From the backoff documentation (https://pypi.python.org/pypi/backoff),
# set maximum number of tries on a failed download:
@backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=8)
# From the ratelimit documentation (https://pypi.python.org/pypi/ratelimit),
# set the rate limit (in seconds) for API calls:
# Following https://github.com/tomasbasham/ratelimit/blob/master/README.rst,
# running @rate_limited(1, 5) will allow the API to be called 1 time every 5
# seconds. Similarly, using @rate_limited(5, 1) will allow the API to be
# called 5 times every 1 second.
@rate_limited(period=5, every=1)
def create_api_request(
        item_doi,
        api_base_url,
        api_request_parameters={},
        custom_user_agent_string=None):
    """Given an item DOI (lacking the 'doi:/' prefix), query an OpenURL
    resolver) and return XML from it."""

    custom_api_query_header = {}
    if custom_user_agent_string:
        custom_api_query_header['user-agent'] = custom_user_agent_string

    # Update the static api parameters to include the (dynamic) DOI:
    api_request_parameters = api_request_parameters.copy()
    api_request_parameters['rft_id'] = f'info:doi/{item_doi}'

    api_response = requests.get(
            api_base_url,
            params=api_request_parameters,
            headers=custom_api_query_header)

    if api_response.status_code != 200:
        raise ErrorWithAPI(
                f'Problem contacting API: We received Status Code '
                '{api_response.status_code}. The full response text is '
                'below: {api_response.text}')

    logging.info(f'Returning query results from URL "{api_response.url}"')

    return api_response

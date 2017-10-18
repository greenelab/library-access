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
@rate_limited(0.2)
def create_api_request(
        item_doi,
        api_base_url,
        static_api_request_parameters_dictionary=None,
        custom_user_agent_string=None):
    """Given an item DOI (lacking the 'doi:/' prefix), query an OpenURL
    resolver) and return XML from it."""

    if static_api_request_parameters_dictionary is None:
        static_api_request_parameters_dictionary = {}

    custom_api_query_header = {}
    if custom_user_agent_string:
        custom_api_query_header['user-agent'] = custom_user_agent_string

    # Update the static api parameters to include the (dynamic) DOI:
    api_request_parameters = static_api_request_parameters_dictionary.copy()
    api_request_parameters.update({
            'rft_id': f'info:doi/{item_doi}'})

    api_response = requests.get(
            api_base_url,
            params=api_request_parameters,
            headers=custom_api_query_header)

    if api_response.status_code != 200:
        raise ErrorWithAPI('Problem contacting API: {}'.format(
                api_response.status_code))

    logging.info(f'Returning query results from URL "{api_response.url}"')

    return api_response

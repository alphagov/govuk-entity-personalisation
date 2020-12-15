import requests
from requests.exceptions import HTTPError


def query_search_api(query, n_results=10, fields=['description']):
    """
    API documentation here:
    https://dataingovernment.blog.gov.uk/2016/05/26/use-the-search-api-to-get-useful-information-about-gov-uk-content/

    :param query: str
    :param n_results: int
    :param fields: list of fields you want from the json
    :return: json
    """

    try:
        resp = requests.get(
            'https://www.gov.uk/api/search.json?q='
            + query
            + '&count='
            + str(n_results)
            + '&fields=' + ','.join(fields), timeout=0.1)
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        return resp.json()['results']

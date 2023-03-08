import requests
import concurrent.futures
from constants import HEADERS

# response.status_code == 200 OK

def get_url(url, page):
    """
    Makes HTTP GET request to singlepage url with headers.

    Args:
        url (str): webpage url;
        page (dict): page to request;

    Return:
        response.json() (list): list with JSON decoded url content.
    """

    params = f'per_page=100&page={page}'
    full_url = f'{url}?{params}'

    response = requests.get(full_url, headers=HEADERS)

    response.raise_for_status()

    return response.json()

def get_multipage_url(url, starting_page=1):
    """
    Makes HTTP GET request to multipage url with headers.

    Args:
        url (str): webpage url;
        starting_page (int): first page to request;

    Return:
        response (list): list with JSON decoded multipage url content.
        num_of_pages (int): max page in the response
    """

    response = []
    num_of_pages = requests.get(f'{url}?per_page=100', headers=HEADERS) 
    num_of_pages = int(num_of_pages.headers['x-Total-Pages'])
        
    if starting_page <= num_of_pages:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(
                get_url, [url] * num_of_pages, range(starting_page, num_of_pages + 1))

        for page in results:
            response += page

        return response, num_of_pages

if __name__ == '__main__':
    pass

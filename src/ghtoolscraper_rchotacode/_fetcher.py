import requests
import json
from ghtoolscraper_rchotacode._rate_limit_exception import RateLimitException
from base64 import b64decode

def fetch_page(query : str, page : int = 1, per_page : int = 10, headers : dict = None) -> dict:
    url = f"https://api.github.com/search/repositories?q={query}&page={page}&per_page={per_page}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 403:
            raise RateLimitException("Rate limit exceeded. Please try again later.")
        else:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")
    
    response = json.loads(response.text)
    if 'items' in response:
        return {
            'total_count' : response.get('total_count', 0),
            'items' : response['items'],
        }
    return {
        'total_count' : 0,
        'items' : [],
    }

def fetch_repo(url : str, headers: dict) -> dict:
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 403:
            raise RateLimitException("Rate limit exceeded. Please try again later.")
        else:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    return json.loads(response.text)    

def fetch_content(url : str, headers: dict) -> str:
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 403:
            raise RateLimitException("Rate limit exceeded. Please try again later.")
        else:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    return b64decode(response.json().get('content', ''))
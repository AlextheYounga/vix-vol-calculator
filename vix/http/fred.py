from bs4 import BeautifulSoup
import sys
import requests

def send_request(url: str) -> any:
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except:
        raise Exception('HTTP Error when scraping Fred website: ', sys.exc_info())
    
    return response

def scrape_3m_treasury_from_fred() -> float:
    """
    Scrapes the St Louis Fed website for the current 3m treasury yield.
    """

    url = 'https://fred.stlouisfed.org/series/DTB3'
    response = send_request(url)

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        treasury_rate = soup.find("span", {"class": "series-meta-observation-value"}).text
    except:
        raise Exception('Error when parsing Fred website: ', sys.exc_info())

    return float(treasury_rate)


def scrape_vix_from_fred() -> float:
    """
    Scrapes the St Louis Fed website for the current 3m treasury yield.
    """

    url = 'https://fred.stlouisfed.org/series/VIXCLS'
    response = send_request(url)

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        spx_vix = soup.find("span", {"class": "series-meta-observation-value"}).text
    except:
        raise Exception('Error when parsing Fred website: ', sys.exc_info())

    return float(spx_vix)
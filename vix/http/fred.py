from bs4 import BeautifulSoup
import os
import sys
import json
import requests
import datetime


class Fred:
    """
    Rates are automatically cached for one day, as the Fred website only updates once per day anyway.
    """
    def __init__(self, debug: bool = False, cache: bool = True):
        self.debug = debug
        self.cache = cache
        self.timestamp = datetime.datetime.now()

    def send_request(self, url: str) -> any:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print('Error when parsing Fred website: ', e)
            return False

        return response

    def scrape_3m_treasury(self) -> float:
        """
        Scrapes the St Louis Fed website for the current 3m treasury yield.
        """

        if self.debug: return 4.87

        if self.cache:
            cached_rates = self.__check_rates_cache()
            if cached_rates: return float(cached_rates['rate'])

        url = 'https://fred.stlouisfed.org/series/DTB3'
        response = self.send_request(url)
        if (not response): return False

        soup = BeautifulSoup(response.text, 'html.parser')
        treasury_rate = soup.find("span", {"class": "series-meta-observation-value"}).text
        self.__cache_rates_data(float(treasury_rate))
        return float(treasury_rate)

    def __cache_rates_data(self, value: float) -> bool:
        cache_directory = 'storage/cache/rates/'
        timestamp_string = datetime.datetime.strftime(self.timestamp, '%Y-%m-%d')
        cache_file = f"{cache_directory}/rates_{timestamp_string}.json"

        if os.path.exists(cache_directory) == False:
            os.makedirs(cache_directory)

        cache_data = {
            'rate': value,
            "timestamp": datetime.datetime.strftime(self.timestamp, '%Y-%m-%d')
        }

        try:
            with open(cache_file, 'w') as f:
                f.write(json.dumps(cache_data))
            return True
        except Exception as e:
            print('Error when caching rates data: ', e)
            return False

    def __check_rates_cache(self) -> dict | bool:
        cache_directory = 'storage/cache/rates/'
        timestamp_string = datetime.datetime.strftime(self.timestamp, '%Y-%m-%d')
        cache_file = f"{cache_directory}/rates_{timestamp_string}.json"

        if not os.path.exists(cache_directory): return False

        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.loads(f.read())
            except Exception as e:
                print('Error when decoding rates cache data: ', e)

        return False

    def scrape_vix(self) -> float:
        """
        This is only used for testing purposes.
        Scrapes the St Louis Fed website for the current vix vol number. 
        """

        url = 'https://fred.stlouisfed.org/series/VIXCLS'
        response = self.send_request(url)

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            spx_vix = soup.find("span", {"class": "series-meta-observation-value"}).text
        except Exception as e:
            print('Error when parsing Fred website: ', e)

        return float(spx_vix)

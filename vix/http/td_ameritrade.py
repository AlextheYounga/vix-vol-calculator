import datetime
import requests
import json
import os


class TDAmeritrade:
    """
    Responses from TD Ameritrade are cached in storage/cache/td/. 
    These responses can be pretty large, like 10MB large, so we generally don't want to be fetching them everytime.
    We will refer to the cached response for 1 day, and then fetch a new one to keep the data accurate.
    When using the cached data, you will still notice differences in the responses; this is because time is a factor.
    """

    def __init__(self, ticker: str, api_key: str, cache: bool = True, debug: bool = False):
        self.ticker = ticker
        self.api_key = api_key
        self.cache = cache
        self.debug = debug
        self.domain = 'api.tdameritrade.com/v1/marketdata'

    def get_option_chain(self, time_range: list) -> dict:
        """
        Fetches the option chain (calls and puts), for a ticker from TD Ameritrade.

        Parameters
        ----------
        ticker      :string
        time_range   :list
                    List containing [from_date, to_date], each as datetime.datetime 

        Returns
        -------
        chain    :dict 
                Dictionary containing the option chain for the ticker.
        """

        if self.debug: return self.__return_sample_response()

        formatted_time_range = self.__format_date(time_range)
        from_date, to_date = formatted_time_range

        cached_data = self.__check_cache(self.ticker, formatted_time_range)
        if cached_data: return cached_data

        url = f"https://{self.domain}/chains?apikey={self.api_key}&symbol={self.ticker}&from_date={from_date}&to_date={to_date}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            chain = response.json()

            if isinstance(chain, dict):
                if self.cache:
                    self.__cache_response(self.ticker, chain, formatted_time_range)
                return chain

            else:
                raise Exception('Error in getOptionChain(). Response is not a dict.')
        except Exception as e:
            raise Exception('TDAmeritrade API Error: ', e)

    def __check_cache(self, ticker: str, time_range: tuple) -> dict:
        """
        Checks the cache for a response from the TD Ameritrade API.

        Parameters
        ----------
        ticker  :str
                The ticker symbol for the response.

        Returns
        -------
        chain   :dict
                The response from the TD Ameritrade API
        """
        cache_directory = 'storage/cache/td/'
        filename = f"{ticker}_{'_'.join(time_range)}.json"
        cache_file = f"{cache_directory}/{filename}"

        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.loads(f.read())
        else:
            return False

    def __cache_response(self, ticker: str, chain: dict, time_range: tuple) -> bool:
        """
        Caches the response from the TD Ameritrade API.

        Parameters
        ----------
        chain   :dict
                The response from the TD Ameritrade API
        ticker  :str
                The ticker symbol for the response.

        Returns
        -------
        bool    :bool
                True if the response was cached successfully, False otherwise.
        """
        cache_directory = 'storage/cache/td/'
        filename = f"{ticker}_{'_'.join(time_range)}.json"
        cache_file = f"{cache_directory}/{filename}"

        if os.path.exists(cache_directory) == False:
            os.makedirs(cache_directory)

        try:
            with open(cache_file, 'w') as f:
                f.write(json.dumps(chain))
            return True
        except Exception as e:
            print('Error when caching TD Ameritrade response: ', e)
            return False

    def __return_sample_response(self):
        txtfile = open('tests/fixtures/sample_td_spx_response.json', "r")
        return json.loads(txtfile.read())

    def __format_date(self, dates: list) -> tuple:
        results = []
        for date in dates:
            fdate = datetime.datetime.strftime(date, '%Y-%m-%d')
            results.append(fdate)

        return tuple(results)

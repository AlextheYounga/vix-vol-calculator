import datetime
from dotenv import load_dotenv
import requests
import json
import sys
import os
load_dotenv()


class TDAmeritrade:
    def get_option_chain(self, ticker: str, time_range: list) -> dict:
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

        if ticker == '__TEST__':
            return self.return_sample_response()

        from_date, to_date = self.__format_date(time_range)
        domain = 'api.tdameritrade.com/v1/marketdata'
        key = os.environ.get("TDAMER_KEY")
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML'
        }

        url = f"https://{domain}/chains?apikey={key}&symbol={ticker}&from_date={from_date}&to_date={to_date}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            chain = response.json()
            if isinstance(chain, dict):
                return chain
            else:
                raise Exception('Error in getOptionChain(). Response is not a dict.')
        except:
            raise Exception('TDAmeritrade API Error: ', sys.exc_info())

    def return_sample_response(self):
        txtfile = open('tests/fixtures/sample_td_spx_response.json', "r")
        return json.loads(txtfile.read())

    def __format_date(self, dates: list) -> tuple:
        results = []
        for date in dates:
            fdate = datetime.datetime.strftime(date, '%Y-%m-%d')
            results.append(fdate)

        return tuple(results)

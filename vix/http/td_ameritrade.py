import datetime
from dotenv import load_dotenv
import requests
import sys
import os
load_dotenv()


class TDAmeritrade: 
    def get_option_chain(self, ticker, time_range):
        """
        Fetches the option chain (calls and puts), for a ticker from TD Ameritrade.

        Parameters
        ----------
        ticker      :string
        time_range   :list
                    List containing [from_date, to_date], each as datetime.datetime 

        Returns
        -------
        list of option expiration dates
        """

        from_date, to_date = self.__format_date(time_range)
        domain = 'api.tdameritrade.com/v1/marketdata'
        key = os.environ.get("TDAMER_KEY")
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML'
        }    
            
        url = 'https://{}/chains?apikey={}&symbol={}&from_date={}&to_date={}'.format(
            domain,
            key,
            ticker,
            from_date,
            to_date
        )

        chain = requests.get(url, headers=headers).json()
        if isinstance(chain, dict):
            return chain
        else:        
            print(chain)
            sys.exit()
    
    def __format_date(self, dates):
        results = []
        for date in dates:
            if (isinstance(date, datetime.datetime)):
                fdate = datetime.datetime.strftime(date, '%Y-%m-%d')
                results.append(fdate)
            else:
                print('Failure in getOptionChain(). Date param must be of type datetime.datetime. Closing program...')
                sys.exit()
        return tuple(results)

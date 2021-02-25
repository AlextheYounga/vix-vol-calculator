import datetime
from dotenv import load_dotenv
import requests
import sys
import json
import os
load_dotenv()


def getOptionChainTD(ticker, timeRange):
    """
    Fetches the option chain (calls and puts), for a ticker from TD Ameritrade.

    Parameters
    ----------
    ticker      :string
    timeRange   :list
                List containing [fromDate, toDate], each as datetime.datetime 

    Returns
    -------
    list of option expiration dates
    """
    def formatDate(dates):
        results = []
        for date in dates:
            if (isinstance(date, datetime.datetime)):
                fdate = datetime.datetime.strftime(date, '%Y-%m-%d')
                results.append(fdate)
            else:
                print('Failure in getOptionChain(). Date param must be of type datetime.datetime. Closing program...')
                sys.exit()
        return tuple(results)

    fromDate, toDate = formatDate(timeRange)
    domain = 'api.tdameritrade.com/v1/marketdata'
    key = os.environ.get("TDAMER_KEY")
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML'
    }        
    url = 'https://{}/chains?apikey={}&symbol={}&fromDate={}&toDate={}'.format(
        domain,
        key,
        ticker,
        fromDate,
        toDate
    )
    chain = requests.get(url, headers=headers).json()
    if isinstance(chain, dict):
        return chain
    else:        
        print(chain)
        sys.exit()

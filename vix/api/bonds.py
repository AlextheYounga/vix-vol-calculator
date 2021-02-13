from datetime import datetime, time, timedelta
from dotenv import load_dotenv
import requests
import sys
import json
import os
load_dotenv()


def get3mTreasury(sandbox=False):
    domain = 'cloud.iexapis.com'
    key = os.environ.get("IEX_TOKEN")
    if (sandbox):
        domain = 'sandbox.iexapis.com'
        key = os.environ.get("IEX_SANDBOX_TOKEN")

    try:
        url = 'https://{}/stable/time-series/treasury/DGS3MO?token={}'.format(
            domain,
            key,
        )
        treasury = requests.get(url).json()
    except:
        #print("Unexpected error:", sys.exc_info()[0])
        return None

    return treasury

import datetime
from pytz import timezone
from math import e

def calculate_t(selected_chain: dict) -> tuple[dict, dict]:
    """
    T = {MCurrent day + MSettlement day + MOther days}/ Minutes in a year 
    https://www.sfu.ca/~poitras/419_VIX.pdf (page 5)
    """
    # Fetching dates from selected_chain
    selected_dates = {
        'nearTerm': selected_chain['nearTerm']['call']['dateInfo'],
        'nextTerm': selected_chain['nextTerm']['call']['dateInfo']
    }

    # Some time variables we will need
    now = timezone('US/Central').localize(datetime.datetime.now())
    midnight = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0)
    minutes_to_midnight = ((midnight - now).seconds / 60)  # MCurrentDay
    minutes_in_year = 525600

    t = {}
    tminutes = {}

    for term, date_info in selected_dates.items():
        minutes_from_now = abs(date_info['dateTimeZone'] - now).total_seconds()  # Calculating diff in seconds
        minutes_to_expire = (minutes_from_now / 60)  # MOther days
        
        expiration_hour = date_info['dateTimeZone'].hour
        minutes_to_settlement_day = (expiration_hour * 60) - 60 # 1 hour before opening or closing depending on the option

        tminutes[term] = minutes_to_expire
        t[term] = (minutes_to_midnight + minutes_to_settlement_day + minutes_to_expire) / minutes_in_year  # T equation

    return t, tminutes


def calculate_f(t: dict, r: float, forward_level: dict) -> dict:
    """
    F = Strike Price + eRT × (Call Price – Put Price)
    "Determine the forward SPX level, F, by identifying the strike price at which the
    absolute difference between the call and put prices is smallest."
    https://www.sfu.ca/~poitras/419_VIX.pdf

    """
    f = {}

    strike_price = forward_level['nearTerm'][0]['strikePrice']

    for term in ['nearTerm', 'nextTerm']:
        call_price = forward_level[term][0]['last']
        put_price = forward_level[term][1]['last']
        f[term] = strike_price + pow(e, r*t[term]) * (call_price - put_price)  # F equation

    return f
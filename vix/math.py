import datetime
from pytz import timezone
from math import e

def calculate_t(selected_chain):
    """
    T = {MCurrent day + MSettlement day + MOther days}/ Minutes in a year 
    https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx
    """
    # Fetching dates from selected_chain
    selected_dates = {
        'nearTerm': selected_chain['nearTerm']['call']['dateInfo'],
        'nextTerm': selected_chain['nextTerm']['call']['dateInfo']
    }

    # Some variables we will need
    now = timezone('US/Central').localize(datetime.datetime.now())
    midnight = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0)
    minutes_to_midnight = ((midnight - now).seconds / 60)  # MCurrentDay
    minutes_to_settlement_day = 510  # minutes from midnight until 8:30 a.m. on {ticker} settlement day
    minutes_in_year = 525600

    t = {}
    tminutes = {}

    for term, date_info in selected_dates.items():
        time_diff = abs(date_info['dateTzObj'] - now).total_seconds()  # Calculating diff in seconds
        minutes_to_expire = (time_diff / 60)  # MOther days
        tminutes[term] = minutes_to_expire
        t[term] = (minutes_to_midnight + minutes_to_settlement_day + minutes_to_expire) / minutes_in_year  # T equation

    return t, tminutes


def calculate_forward_level(selected_chain):
    """
    "Determine the forward SPX level, F, by identifying the strike price at which the
    absolute difference between the call and put prices is smallest."
    https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx

    """
    strikes = {
        'nearTerm': {},
        'nextTerm': {}
    }

    price_diffs = {
        'nearTerm': {},
        'nextTerm': {}
    }

    # Collecting prices on call and put options with strike price as key.
    for term, options in selected_chain.items():
        for side, option in options.items():
            for strike, details in option['strikes'].items():

                if (not strikes[term].get(strike, False)):
                    strikes[term][strike] = []
                strikes[term][strike].append(details[0]['last'])

    # Collect price differences from call and put options.
    for term, strike in strikes.items():
        for strike_price, prices in strike.items():
            if (len(prices) == 2):
                p1 = prices[0]
                p2 = prices[1]

                if ((0 in [p1, p2]) == False):
                    diff = abs(p1 - p2)
                    price_diffs[term][diff] = strike_price

    # Select the smallest price difference out of the bunch.
    near_term_strike = price_diffs['nearTerm'][min(price_diffs['nearTerm'].keys())]
    next_term_strike = price_diffs['nextTerm'][min(price_diffs['nextTerm'].keys())]

    forwardLevel = {
        'nearTerm': [
            selected_chain['nearTerm']['call']['strikes'][near_term_strike][0],
            selected_chain['nearTerm']['put']['strikes'][near_term_strike][0],
        ],
        'nextTerm': [
            selected_chain['nextTerm']['call']['strikes'][next_term_strike][0],
            selected_chain['nextTerm']['put']['strikes'][next_term_strike][0],
        ]
    }

    return forwardLevel
    

def calculate_f(t, r, forward_level):
    """
    F = Strike Price + eRT × (Call Price – Put Price)
    "Determine the forward SPX level, F, by identifying the strike price at which the
    absolute difference between the call and put prices is smallest."
    https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx

    """
    f = {}

    strike_price = forward_level['nearTerm'][0]['strikePrice']

    for term in ['nearTerm', 'nextTerm']:
        call_price = forward_level[term][0]['last']
        put_price = forward_level[term][1]['last']
        f[term] = strike_price + pow(e, r*t[term]) * (call_price - put_price)  # F equation

    return f
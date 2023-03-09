import datetime
import calendar
from dateutil.relativedelta import relativedelta

def build_option_chain_time_range() -> list:
    # Building a time_range to send to TD Ameritrade's API
    today = datetime.datetime.now()
    three_months_away = (today + relativedelta(months=+3))
    three_months_away_days = calendar.monthrange(three_months_away.year, three_months_away.month)[1]
    
    from_date = today
    to_date = datetime.datetime(three_months_away.year, three_months_away.month, three_months_away_days)
    time_range = [from_date, to_date]

    return time_range


def determine_forward_level_strike(selected_chain: dict) -> dict:
    """
    "Determine the forward SPX level, F, by identifying the strike price at which the
    absolute difference between the call and put prices is smallest."
    https://www.sfu.ca/~poitras/419_VIX.pdf

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
        for _side, option in options.items():
            for strike, details in option['strikes'].items():

                if (not strikes[term].get(strike, False)):
                    strikes[term][strike] = []
                    
                strikes[term][strike].append(details[0]['last'])

    import pdb; pdb.set_trace()

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
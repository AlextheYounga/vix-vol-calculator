import math
from vix.http.fred import scrape_3m_treasury_from_fred
from vix.http.td_ameritrade import TDAmeritrade
from vix.options.options import build_option_chain_time_range
from vix.options.expirations import Expirations
from vix.math import *
from vix.volatility import Volatility

"""
I have followed the official VIX whitepaper to the best of my ability in the making of this program.
This program uses the TD Ameritrade API to fetch the entire option chain, and fetches the latest
3M Treasury Bond yield (the risk-free interest rate) from the FRED website (https://fred.stlouisfed.org/series/DTB3).

I have attempted to document the process as best as I can. 
https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx
"""


def run_vix_equation(ticker):
    """
    Runs the VIX equation on a ticker.

    Parameters
    ----------
    ticker      :string

    Returns
    -------
    vix         :float
    """

    # Step 1: Fetch the option chain for the ticker.
    time_range = build_option_chain_time_range()
    chain = TDAmeritrade().get_option_chain(ticker, time_range)

    # Step 2
    # Find the proper "near-term" and "next-term" option expirations to be used to find Forward Level.
    # See find_next_two_months_expirations() in functions.py.
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 4)
    selected_chain = Expirations().find_option_terms(chain)

    # Step 3
    # Calculate R
    # The risk-free interest rate, R, is the bond-equivalent yield of the U.S. T-bill maturing
    # closest to the expiration dates of relevant SPX options. As such, the VIX calculation may
    # use different risk-free interest rates for near- and next-term options.
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 4)
    r = scrape_3m_treasury_from_fred()

    # Step 4
    # Calculate T1 and T2, for near-term and next-term options respectively. See calculateT() in functions.py for more.
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 4)
    t, tminutes = calculate_t(selected_chain)

    # Step 5
    # Determine the forward SPX level, F, by identifying the strike price at which the
    # absolute difference between the call and put prices is smallest
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 5)
    forward_level = calculate_forward_level(selected_chain)

    # Step 6
    # Calculate F, where F is the: "forward SPX {but in our case, any ticker} level, by identifying the strike price at which the
    # absolute difference between the call and put prices is smallest."
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 5)
    f = calculate_f(t, r, forward_level)

    # Step 7
    # Calculate Vol
    # Most of this function is finding K0
    # Once you discover K0, you can immediately uncover many more crucial variables used to calculate vol.
    # I decided it would take far more code to break up this function into multiple parts rather than to simply
    # finish it in one loop.
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 6 - 9)
    vol = Volatility().calculate(f, t, r, selected_chain)

    # Step 8
    # Calculate VIX

    minYear = 525600 # Minutes in year
    minMonth = 43200 # Minutes in 30 days
    v1 = vol['nearTerm']
    v2 = vol['nextTerm']
    t1 = t['nearTerm']
    t2 = t['nextTerm']
    nT1 = tminutes['nearTerm']  # Minutes to expiration
    nT2 = tminutes['nextTerm']  # Minutes to expiration


    # Test Data to confirm accuracy
    # NT1 = number of minutes to settlement of the near-term options (12,960)
    # NT2 = number of minutes to settlement of the next-term options (53,280)
    # N30 = number of minutes in 30 days (30 × 1,440 = 43,200)
    # N365 = number of minutes in a 365-day year (365 ×1,440 = 525,600

    # minutesYear = 525600
    # minutesMonth = 43200
    # v1 = 0.4727679
    # v2 = 0.3668180
    # t1 = 0.0246575
    # t2 = 0.1013699
    # nT1 = 12960  # Minutes to expiration
    # nT2 = 53280  # Minutes to expiration

    vix = 100 * math.sqrt(
        (t1 * v1 * ((nT2 - minMonth) / (nT2 - nT1)) + t2 * v2 * ((minMonth - nT1) / (nT2 - nT1))) * minYear / minMonth
    )

    return round(vix, 3)
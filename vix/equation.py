import json
import math
import statistics
import sys
from .api.bonds import get3mTreasury
from .functions import *


def vix_explanation():
    """
    I have followed the official VIX whitepaper to the best of my ability in the making of this program.
    This program uses the TD Ameritrade API to fetch the entire option chain, and the IEX Cloud API to fetch the
    3M Treasury Bond yield, (the risk-free interest rate).

    I have attempted to document the process as best as I can. 
    https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx


    """


def vix_equation(ticker, debug=False):
    """
    Runs the VIX equation on a ticker.

    Parameters
    ----------
    ticker      :string
    sandbox     :bool
                Sets the IEX environment to sandbox mode to make limitless API calls for testing.

    Returns
    -------
    vix         :float
    """

    # Step 1: Fetch the option chain for the ticker.
    chain = collectOptionChain(ticker, debug)

    # Step 2
    # Find the proper "near-term" and "next-term" option expirations to be used to find Forward Level.
    # See selectOptionExpirations() in functions.py.
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 4)
    selectedDates, selectedChain = selectOptionExpirations(chain)

    # Step 3
    # Calculate R
    # The risk-free interest rate, R, is the bond-equivalent yield of the U.S. T-bill maturing
    # closest to the expiration dates of relevant SPX options. As such, the VIX calculation may
    # use different risk-free interest rates for near- and next-term options.
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 4)
    r = get3mTreasury()[0]['value']

    # Step 4
    # Calculate T1 and T2, for near-term and next-term options respectively. See calculateT() in functions.py for more.
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 4)
    t, tminutes = calculateT(selectedDates)

    # Step 5
    # Determine the forward SPX level, F, by identifying the strike price at which the
    # absolute difference between the call and put prices is smallest
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 5)
    forwardLevel = calculateForwardLevel(selectedChain)

    # Step 6
    # Calculate F, where F is the: "forward SPX {but in our case, any ticker} level, by identifying the strike price at which the
    # absolute difference between the call and put prices is smallest."
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 5)
    f = calculateF(t, r, forwardLevel)

    # Step 7
    # Calculate Vol
    # Most of this function is finding K0
    # Once you discover K0, you can immediately uncover many more crucial variables used to calculate vol.
    # I decided it would take far more code to break up this function into multiple parts rather than to simply
    # finish it in one loop.
    # https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx (pg 6 - 9)
    vol = calculateVol(f, t, r, selectedChain)

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

    if (debug):
        print('Minutes Year = '+str(minYear))
        print('Minutes in Month = '+str(minMonth))
        print('Near-Term Vol (v1) = '+str(v1))
        print('Next-Term Vol (v2) = '+str(v2))
        print('T1 = '+str(t1))
        print('T2 = '+str(t2))
        print('Near-Term Expiration Minutes = '+str(nT1))
        print('Next-Term Expiration Minutes = '+str(nT2))
        print("\n")


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

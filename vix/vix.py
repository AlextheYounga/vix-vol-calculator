import math
from vix.http.fred import Fred
from vix.http.td_ameritrade import TDAmeritrade
from vix.options.options import *
from vix.options.expirations import Expirations
from vix.math import *
from vix.volatility import Volatility


class Vix:
    """
    VIX Volatility equation from the official VIX whitepaper.
    This program uses the TD Ameritrade API to fetch the entire option chain of the requested ticker, and fetches the latest
    3M Treasury Bond yield (the risk-free interest rate) from the FRED website (https://fred.stlouisfed.org/series/DTB3).

    VIX Whitepaper:
    https://www.sfu.ca/~poitras/419_VIX.pdf
    """

    def __init__(self, td_api_key: str, caching_enabled: bool = True, debug: bool = False):
        self.api_key = td_api_key
        self.caching_enabled = caching_enabled
        self.debug = debug

    def calculate(self, ticker):
        """
        Runs the VIX equation on a ticker.

        Parameters
        ----------
        ticker      :string

        Returns
        -------
        vix         :float
        """

        chain = self.__build_option_chain(ticker)

        selected_chain = self.__get_near_next_term_options(chain)

        r = self.__get_risk_free_rate()

        t, tminutes = self.__get_t1_t2(selected_chain)

        f = self.__get_forward_level(t, r, selected_chain)

        vol = self.__get_volatility(f, t, r, selected_chain)

        vix = self.__equation(vol, t, tminutes)

        return vix

    def __build_option_chain(self, ticker: str) -> dict:
        # Step 1: Fetch the option chain for the ticker.
        time_range = build_option_chain_time_range()

        td = TDAmeritrade(
            ticker=ticker,
            api_key=self.api_key,
            cache=self.caching_enabled,
            debug=self.debug,
        )

        chain = td.get_option_chain(time_range)
        return chain

    def __get_near_next_term_options(self, chain: dict) -> dict:
        # Step 2
        # Find the proper "near-term" and "next-term" option expirations to be used to find Forward Level.
        # https://www.sfu.ca/~poitras/419_VIX.pdf (pg 4)
        expirations = Expirations()
        selected_chain = expirations.find_option_terms(chain)
        return selected_chain

    def __get_risk_free_rate(self) -> float:
        # Step 3
        # Calculate R
        # The risk-free interest rate, R, is the bond-equivalent yield of the U.S. T-bill maturing
        # closest to the expiration dates of relevant SPX options. As such, the VIX calculation may
        # use different risk-free interest rates for near- and next-term options.
        # https://www.sfu.ca/~poitras/419_VIX.pdf (pg 4)
        fred = Fred(cache=self.caching_enabled, debug=self.debug)
        r = fred.scrape_3m_treasury()

        return r

    def __get_t1_t2(self, selected_chain: dict) -> dict:
        # Step 4
        # Calculate T1 and T2, for near-term and next-term options respectively. See calculateT() in functions.py for more.
        # https://www.sfu.ca/~poitras/419_VIX.pdf (pg 4)
        t, tminutes = calculate_t(selected_chain)
        return t, tminutes

    def __get_forward_level(self, t: dict, r: float, selected_chain: dict) -> dict:
        # Step 5
        # Determine the forward SPX level, (used for F), by identifying the strike price at which the
        # absolute difference between the call and put prices is smallest
        # https://www.sfu.ca/~poitras/419_VIX.pdf (pg 5)
        forward_level = determine_forward_level_strike(selected_chain)

        # Step 6
        # Calculate F, where F is the: "forward SPX {but in our case, any ticker} level, by identifying the strike price at which the
        # absolute difference between the call and put prices is smallest."
        # https://www.sfu.ca/~poitras/419_VIX.pdf (pg 5)
        f = calculate_f(t, r, forward_level)
        return f

    def __get_volatility(self, f: dict, t: dict, r: float, selected_chain: dict) -> dict:
        # Step 7
        # Calculate Vol
        # Most of this function is finding K0
        # Once you discover K0, you can immediately uncover many more crucial variables used to calculate vol.
        # I decided it would take far more code to break up this function into multiple parts rather than to simply
        # finish it in one loop.
        # https://www.sfu.ca/~poitras/419_VIX.pdf (pg 6 - 9)
        vol = Volatility().calculate(f, t, r, selected_chain)
        return vol

    def __equation(self, vol, t, tminutes):
        # Step 8
        # Calculate VIX
        v1 = vol['nearTerm']  # Volatility of near-term options
        v2 = vol['nextTerm']  # Volatility of next-term options
        t1 = t['nearTerm']  # Special VIX calculation for near-term options timing
        t2 = t['nextTerm']  # Special VIX calculation for next-term options timing
        nT1 = tminutes['nearTerm']  # Minutes to expiration
        nT2 = tminutes['nextTerm']  # Minutes to expiration

        minYear = 525600  # Minutes in a year
        minMonth = 43200  # minutes in a month

        # VIX Equation
        vix = 100 * math.sqrt(
            (t1 * v1 * ((nT2 - minMonth) / (nT2 - nT1)) + t2 * v2 * ((minMonth - nT1) / (nT2 - nT1))) * minYear / minMonth
        )

        return round(vix, 3)

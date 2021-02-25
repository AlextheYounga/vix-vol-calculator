import json
import sys
import datetime
import time
import calendar
from math import e
from pytz import timezone
import colored
from colored import stylize
from dateutil.relativedelta import relativedelta
from .api.options import getOptionChainTD
import calendar


def collectOptionChain(ticker, debug):
    today = datetime.datetime.now()
    three_months_away = (today + relativedelta(months=+3))
    three_months_away_days = calendar.monthrange(three_months_away.year, three_months_away.month)[1]

    # Building a timerange to send to TD Ameritrade's API
    fromDate = today
    toDate = datetime.datetime(three_months_away.year, three_months_away.month, three_months_away_days)
    timeRange = [fromDate, toDate]

    """ Step 1: Fetch the option chain from TD Ameritrade """
    if (debug):
        # Test Data
        JSON = 'vix/sample_response/response.json'
        with open(JSON) as jsonfile:
            chain = json.loads(jsonfile.read())
            return chain

    chain = getOptionChainTD(ticker, timeRange)
    return chain


def selectOptionExpirations(chain):
    """
    1. Fetches all option expiration dates from IEX api. 
    2. Finds this month's expiration and next months expiration (the near-term and next-term expirations).
    3. Calculates and returns a dict containing the near-term and next-term expiration dates, along with the 
    option chain for those dates. 
    """

    if (chain):
        today = datetime.datetime.now()

        # Our container for collecting our near-term/next-term options
        options = {}

        """ Step 2: Finding this month's and next month's closest option expiration dates. """
        for optionSide in ['callExpDateMap', 'putExpDateMap']:
            for expir, strikes in chain[optionSide].items():  # Looping each side of the option chain

                if (optionSide not in options):
                    options[optionSide] = {}

                expDate = datetime.datetime.strptime(expir.split(':')[0], '%Y-%m-%d')  # Option expiration date object
                # Just grabbing the first strike row in the chain because TD has specific information on
                # this nested level of the dict. I can get the precise expiration from any strike.
                firstStrike = next(iter(strikes.values()))[0]
                daysToExpiration = int(firstStrike['daysToExpiration'])
                preciseExpiration = int(firstStrike['expirationDate'])  # Getting precise expiration

                if (daysToExpiration > 7):  # Must be at least 7 days from expiration.
                    options[optionSide][preciseExpiration] = {
                        'dateInfo': {
                            'expDate': expDate,
                            'month': expDate.month,
                            'preciseExpiration': preciseExpiration,
                            'daysToExpiration': daysToExpiration,
                        },
                        'strikes': strikes
                    }

        """
        Step 3: Calculating the nearest option of each group of options, 
        finding min() value of each group's keys, which again, are the time to expiration in seconds.
        """

        def vixExpirationRules(options):
            """
            For SPX, the VIX specifies that the next-term options can be no longer than 2 months away. This doesn't
            work for all stocks, because not all stocks have option expirations each month. This caused me some trouble
            when I originall built this, so I have extended the max time period outwards to 3 months. This equation likely
            won't be very useful for anything farther in the future. This technique still works fine for SPX. 
            """
            this_month = today.month
            next_month = (today + relativedelta(months=+1))
            two_months_away = (today + relativedelta(months=+2))
            three_months_away = (today + relativedelta(months=+3))

            month_0 = []
            month_1 = []
            month_2 = []
            month_3 = []
            for side, option in options.items():
                for exp, data in option.items():
                    if (data['dateInfo']['month'] == this_month):
                        month_0.append(exp)
                    if (data['dateInfo']['month'] == next_month.month):
                        month_1.append(exp)
                    if (data['dateInfo']['month'] == two_months_away.month):
                        month_3.append(exp)
                    if (data['dateInfo']['month'] == three_months_away.month):
                        month_3.append(exp)

            if (len(month_0) != 0):
                nearTermExp = min(month_0)
                flat_list = [item for sublist in [month_1, month_2, month_3] for item in sublist]
                if (len(flat_list) > 0):
                    nextTermExp = min(flat_list)
                    return {'nearTerm': nearTermExp, 'nextTerm': nextTermExp}
            if (len(month_1) != 0):
                nearTermExp = min(month_1)
                flat_list = [item for sublist in [month_2, month_3] for item in sublist]
                if (len(flat_list) > 0):
                    nextTermExp = min(flat_list)
                    return {'nearTerm': nearTermExp, 'nextTerm': nextTermExp}
            if (len(month_2) != 0):
                nearTermExp = min(month_2)
                if (len(month_3) > 0):
                    nextTermExp = min(month_3)
                    return {'nearTerm': nearTermExp, 'nextTerm': nextTermExp}

            # If not enough option data, end program. We can go no further.
            print(stylize("Not enough option data for ticker to make a useful measurement.", colored.fg("red")))
            sys.exit()

        properExpir = vixExpirationRules(options)

        selectedChain = {}
        for term in ['nearTerm', 'nextTerm']:
            # Selecting the proper calls and puts from option dictionary.
            selectedChain[term] = {
                'call': options['callExpDateMap'][properExpir[term]],
                'put': options['putExpDateMap'][properExpir[term]],
            }

        # Date timezone manipulation; doing here because we'll need these later.
        for term, side in selectedChain.items():
            for k, data in side.items():
                t = data['dateInfo']['preciseExpiration']
                dateT = datetime.datetime.fromtimestamp(float(t / 1000))  # Windows workaround
                # The previous division by 1000 is simply a workaround for Windows. Windows doesn't seem to play nice
                # with timestamps in miliseconds.
                dateObj = timezone('US/Central').localize(dateT)  # Converting to timezone
                dateStr = dateObj.strftime('%Y-%m-%d')

                selectedChain[term][k]['dateInfo']['dateTzObj'] = dateObj
                selectedChain[term][k]['dateInfo']['dateStr'] = dateStr

        return selectedChain


def calculateForwardLevel(selectedChain):
    """
    "Determine the forward SPX level, F, by identifying the strike price at which the
    absolute difference between the call and put prices is smallest."
    https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx

    """
    strikes = {
        'nearTerm': {},
        'nextTerm': {}
    }

    priceDiffs = {
        'nearTerm': {},
        'nextTerm': {}
    }

    # Collecting prices on call and put options with strike price as key.
    for term, options in selectedChain.items():
        for side, option in options.items():
            for strike, details in option['strikes'].items():

                if (not strikes[term].get(strike, False)):
                    strikes[term][strike] = []
                strikes[term][strike].append(details[0]['last'])

    # Collect price differences from call and put options.
    for term, strike in strikes.items():
        for strprice, prices in strike.items():
            if (len(prices) == 2):
                p1 = prices[0]
                p2 = prices[1]

                if ((0 in [p1, p2]) == False):
                    diff = abs(p1 - p2)
                    priceDiffs[term][diff] = strprice

    # Select the smallest price difference out of the bunch.
    nearTermStrike = priceDiffs['nearTerm'][min(priceDiffs['nearTerm'].keys())]
    nextTermStrike = priceDiffs['nextTerm'][min(priceDiffs['nextTerm'].keys())]

    forwardLevel = {
        'nearTerm': [
            selectedChain['nearTerm']['call']['strikes'][nearTermStrike][0],
            selectedChain['nearTerm']['put']['strikes'][nearTermStrike][0],
        ],
        'nextTerm': [
            selectedChain['nextTerm']['call']['strikes'][nextTermStrike][0],
            selectedChain['nextTerm']['put']['strikes'][nextTermStrike][0],
        ]
    }

    return forwardLevel


def calculateT(selectedChain):
    """
    T = {MCurrent day + MSettlement day + MOther days}/ Minutes in a year 
    https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx
    """
    # Fetching dates from selectedChain
    selectedDates = {
        'nearTerm': selectedChain['nearTerm']['call']['dateInfo'],
        'nextTerm': selectedChain['nextTerm']['call']['dateInfo']
    }

    # Some variables we will need
    now = timezone('US/Central').localize(datetime.datetime.now())
    midnight = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0)
    minutesToMidnight = ((midnight - now).seconds / 60)  # MCurrentDay
    mSettlementDay = 510  # minutes from midnight until 8:30 a.m. on {ticker} settlement day
    minutesYear = 525600

    t = {}
    tminutes = {}

    for term, dateInfo in selectedDates.items():
        timeDiff = abs(dateInfo['dateTzObj'] - now).total_seconds()  # Calculating diff in seconds
        minutesToExpire = (timeDiff / 60)  # MOther days
        tminutes[term] = minutesToExpire
        t[term] = (minutesToMidnight + mSettlementDay + minutesToExpire) / minutesYear  # T equation

    return t, tminutes


def calculateF(t, r, forwardLevel):
    """
    F = Strike Price + eRT × (Call Price – Put Price)
    "Determine the forward SPX level, F, by identifying the strike price at which the
    absolute difference between the call and put prices is smallest."
    https://www.optionseducation.org/referencelibrary/white-papers/page-assets/vixwhite.aspx

    """
    f = {}

    strikePrice = forwardLevel['nearTerm'][0]['strikePrice']

    for term in ['nearTerm', 'nextTerm']:
        callPrice = forwardLevel[term][0]['last']
        putPrice = forwardLevel[term][1]['last']
        f[term] = strikePrice + pow(e, r*t[term]) * (callPrice - putPrice)  # F equation

    return f


def calculateVol(f, t, r, selectedChain):
    """
    """

    vol = {}
    for term, options in selectedChain.items():

        def calculateK0(term, options, f=f[term]):
            ks = {}  # As in many k's. A collection of k's, (contracts within VIX parameters)

            for side, option in options.items():
                ks[side] = {}
                for strike, details in option['strikes'].items():

                    # Collecting bids and asks to be used in determining 'ki'
                    bid = details[0]['bid']
                    ask = details[0]['ask']
                    ks[side][strike] = {
                        'bid': bid,
                        'ask': ask,
                        'midquote': (bid + ask) / 2
                    }

                    # Collecting k0
                    # The first strike below the forward index level, F
                    minFwdLvl = float(int(f))
                    if (float(strike) <= minFwdLvl):
                        k0 = strike
            return k0, ks

        def calculateBounds(k0, ks):
            """
            Finding upper and lower boundaries on chain
            "Select out-of-the-money put options with strike prices < K0. Start with the put
            strike immediately lower than K0 and move to successively lower strike prices.
            Exclude any put option that has a bid price equal to zero (i.e., no bid). As shown
            below, once two puts with consecutive strike prices are found to have zero bid
            prices, no puts with lower strikes are considered for inclusion."
            """
            bounds = {}
            for side, strikes in ks.items():
                zeros = 0
                strklist = strikes.keys()
                if (side == 'put'):
                    strklist = list(reversed(strikes.keys()))
                for strike in strklist:

                    if ((side == 'put') and (strike > k0)):  # Excluding all put prices above k0
                        continue
                    if ((side == 'call') and (strike < k0)):  # Ecluding all call prices below k0
                        continue

                    if (zeros == 2):  # If two zero bids are encountered in a row, our answer will be the last ki set.
                        break

                    b = ks[side][strike]['bid']
                    a = ks[side][strike]['ask']

                    if (b and a):
                        bounds[side] = strike
                    else:
                        zeros += 1

            return bounds

        def buildVixChain(k0, ks, putCallAvg):
            """
            Building a new chain excluding all contracts outside of the bounds above.
            """
            vixChain = []
            for side, strikes in ks.items():
                for strike, data in strikes.items():
                    if (side == 'call'):
                        if ((strike < k0) or (strike > bounds['call'])):
                            continue
                    if (side == 'put'):
                        if ((strike > k0) or (strike < bounds['put'])):
                            continue
                    ki = {
                        'side': side,
                        'strike': strike,
                        'bid': data['bid'],
                        'ask': data['ask'],
                        'midquote': data['midquote'],
                    }

                    # "The K0 put and call prices are averaged to produce a single value"
                    if (strike == k0):
                        ki['midquote'] = putCallAvg

                    vixChain.append(ki)

            return vixChain

        def calculateStrikeContributions(r, t, vixChain):
            """
            Determining ∆Ki
            "Generally, ∆Ki is half the difference between the strike prices on either side of Ki. For
            example, the ∆K for the next-term 300 Put is 75: ∆K300 Put = (350 – 200)/2. At the upper
            and lower edges of any given strip of options, ∆Ki is simply the difference between Ki and
            the adjacent strike price."
            """

            contributions = []  # Building a list of the "Contribution by Strike"
            vc = sorted(vixChain, key=lambda i: i['strike'])
            for i, kdata in enumerate(vc):

                strkAbove = float(vc[i + 1]['strike']) if (0 <= (i + 1) < len(vc)) else 0
                strkBelow = float(vc[i - 1]['strike']) if (0 <= (i - 1) < len(vc)) else 0
                ki = float(kdata['strike'])
                q = float(kdata['midquote'])

                if (i == 0):
                    deltaK = strkAbove - ki
                elif (i == (len(vc) - 1)):  # Workaround to odd issue with len() after using sorted.
                    deltaK = ki - strkBelow
                else:
                    deltaK = ((strkAbove - strkBelow) / 2)

                # ∆Ki/Ki**2 e**(rt) * q
                kc = deltaK/pow(ki, 2) * pow(e, r*t[term]) * q

                contributions.append(kc)

            return contributions

        k0, ks = calculateK0(term, options)
        bounds = calculateBounds(k0, ks)

        # Collecting put/call averages
        # "Finally, select both the put and call with strike price K0. VIX
        # uses the average of quoted bid and ask, or mid-quote, prices for each option selected. The
        # K0 put and call prices are averaged to produce a single value."
        callMQ = ks['call'][k0]['midquote']
        putMQ = ks['put'][k0]['midquote']
        putCallAvg = (callMQ + putMQ) / 2

        vixChain = buildVixChain(k0, ks, putCallAvg)
        contributions = calculateStrikeContributions(r, t, vixChain)

        # The following is essentially the VIX formula
        # 2/T ∑∆Ki/Ki**2 e**(rt) * q
        sigmaKcT = (2/t[term] * sum(contributions))
        tK = 1/float(t[term]) * pow(((float(f[term]) / float(k0)) - 1), 2)

        v = abs(sigmaKcT - tK)

        vol[term] = v

    return vol

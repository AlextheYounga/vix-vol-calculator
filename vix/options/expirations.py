import datetime
from pytz import timezone
from dateutil.relativedelta import relativedelta
import colored
from colored import stylize
import sys


class Expirations:
    def find_option_terms(self, chain: dict):
        option_terms = self.__find_next_two_months_expirations(chain)
        selected_chain = self.__calculate_nearest_option_of_option_groups(option_terms)

        return selected_chain

    def __find_next_two_months_expirations(self, chain: dict) -> dict:
        """
        Parse the option chain returned from TD Ameritrade.

        Finds this month's expiration and next months expiration (the near-term and next-term expirations).
        Calculates and returns a dict containing the near-term and next-term expiration dates, along with the
        option chain for those dates. 
        """

        # Our container for collecting our near-term/next-term options
        option_terms = {}

        try:
            for option_side in ['callExpDateMap', 'putExpDateMap']:  # Call and Put objects returned from TD Ameritrade
                for expir, strikes in chain[option_side].items():  # Looping each side of the option chain, calls and puts

                    if (option_side not in option_terms):
                        option_terms[option_side] = {}

                    # Option expiration date object
                    datetime_safe_expiration = expir.split(':')[0]
                    expiration_date = datetime.datetime.strptime(datetime_safe_expiration, '%Y-%m-%d')

                    # Grabbing the first strike row in the chain because I can get the precise expiration from any strike.
                    # TD Ameritrade adds the expiration date to every row
                    firstStrike = next(iter(strikes.values()))[0]
                    daysToExpiration = int(firstStrike['daysToExpiration'])
                    precise_expiration = int(firstStrike['expirationDate'])  # Getting precise expiration

                    if (daysToExpiration > 7):  # Must be at least 7 days from expiration, VIX rule.
                        option_terms[option_side][precise_expiration] = {
                            'dateInfo': {
                                'expirationDate': expiration_date,
                                'month': expiration_date.month,
                                'preciseExpiration': precise_expiration,
                                'daysToExpiration': daysToExpiration,
                            },
                            'strikes': strikes
                        }
        except:
            raise Exception(
                'There has been a change in the TD Ameritrade API. See __find_next_two_months_expirations()',
                sys.exc_info()
            )

        return option_terms

    def __calculate_nearest_option_of_option_groups(self, option_terms: dict) -> dict:
        """
        Calculating the nearest option of each group of options, 
        finding min() value of each group's keys, which are the time to expiration in seconds.
        """
        proper_expiration = self.__vix_expiration_rules(option_terms)

        selected_chain = {}
        for term in ['nearTerm', 'nextTerm']:
            # Selecting the proper calls and puts from option dictionary.
            selected_chain[term] = {
                'call': option_terms['callExpDateMap'][proper_expiration[term]],
                'put': option_terms['putExpDateMap'][proper_expiration[term]],
            }

        # Date timezone manipulation; doing here because we'll need these later.
        for term, side in selected_chain.items():
            for k, data in side.items():
                t = data['dateInfo']['preciseExpiration']  # TD Ameritrade object
                dateT = datetime.datetime.fromtimestamp(float(t / 1000))  # Windows workaround
                # The previous division by 1000 is simply a workaround for Windows. Windows doesn't seem to play nice
                # with timestamps in miliseconds.
                dateTzObj = timezone('US/Central').localize(dateT)  # Converting to Chicago timezone
                dateStr = dateTzObj.strftime('%Y-%m-%d')

                selected_chain[term][k]['dateInfo']['dateTzObj'] = dateTzObj
                selected_chain[term][k]['dateInfo']['dateStr'] = dateStr

        return selected_chain

    def __vix_expiration_rules(self, option_terms: dict) -> dict:
        """
        For SPX, the VIX specifies that the next-term options can be no longer than *2 months away. This time range doesn't
        work for all stocks, because not all stocks have option expirations each month. Some have expirations every 3 months, some every 6 months. 
        This caused me some trouble when I originally built this, so I have extended the max time period outwards to 3 months. Unfortunately, at the
        moment, this equation won't support any stock that doesn't have expirations in the coming 3 months.
        """
        today = datetime.datetime.now()
        this_month = today.month
        next_month = (today + relativedelta(months=+1))
        two_months_away = (today + relativedelta(months=+2))
        three_months_away = (today + relativedelta(months=+3))

        month_0 = []
        month_1 = []
        month_2 = []
        month_3 = []

        for _side, option in option_terms.items():
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
        raise Exception('Not enough option data for ticker to make a useful measurement.')

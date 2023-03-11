import datetime
from pytz import timezone
from dateutil.relativedelta import relativedelta
import colored
from colored import stylize
import sys


class Expirations:
    def find_option_terms(self, chain: dict):
        option_terms = self.__consolidate_option_terms(chain)
        vix_expirations = self.__select_option_terms_from_vix_expiration_rules(option_terms)
        selected_chain = self.__select_near_next_calls_and_puts(option_terms, vix_expirations)

        return selected_chain


    def __consolidate_option_terms(self, chain: dict) -> dict:
        option_terms = {}
        try:
            for option_side in ['callExpDateMap', 'putExpDateMap']:
                for expiration, strikes in chain[option_side].items():  # Looping each side of the option chain, calls and puts

                    if (option_side not in option_terms):
                        option_terms[option_side] = {}

                    # Grabbing the first strike row in the chain because I can get the precise expiration from any strike.
                    # TD Ameritrade adds the expiration date to every row
                    firstStrike = next(iter(strikes.values()))[0]
                    human_readable_expiration = expiration.split(':')[0] # Ex: "2023-03-09:1" Expiration with index (date:index)
                    days_to_expiration = int(firstStrike['daysToExpiration'])
                    precise_expiration = int(firstStrike['expirationDate'])  # Getting precise expiration
                    datetime_expiration = datetime.datetime.fromtimestamp(float(precise_expiration / 1000))
                    date_timezone = timezone('US/Central').localize(datetime_expiration)

                    if (days_to_expiration > 7):  # Must be at least 7 days from expiration, VIX rule.
                        option_terms[option_side][precise_expiration] = {
                            'dateInfo': {
                                'expirationDate': human_readable_expiration,
                                'month': datetime_expiration.month,
                                'expirationTimestamp': precise_expiration,
                                'daysToExpiration': days_to_expiration,
                                'dateTimeExpiration': datetime_expiration,
                                'dateTimeZone': date_timezone
                            },
                            'strikes': strikes
                        }
        except:
            raise Exception(
                'There has been a change in the TD Ameritrade API. See __find_next_two_months_expirations()',
                sys.exc_info()
            )

        return option_terms

    
    def __select_option_terms_from_vix_expiration_rules(self, option_terms: dict) -> dict:
        """
        The components of the VIX Index are near- and next-term put and call options with more than 23 days and less than 37 days to expiration.
        These near- and next-term option expirations must have at least 7 days between them. This expiration rule does not cleanly apply to all assets 
        because most stocks do not have as many option contracts as the S&P500. To allow this equation to be applied to *most stocks, I am extending the 
        max possible next-term expiration to 3 months, although if there is a next-term expiration that is less than 37 days, that will be used instead.
        """

        vix_expirations = []

        min_near_term_expiration_days = 23
        hard_cuttoff_expiration_days = 120 # hard cutoff is 120 days to allow for stocks other than S&P, but we will take less if we can

        # Expiration dates are the same for calls and puts, just need to loop one of them.
        try: 
            for expiration, data in option_terms['callExpDateMap'].items():
                days_to_expiration = data['dateInfo']['daysToExpiration']
                # Rules: 
                # 1. Must be at least 23 days from expiration
                # 2. Preferred to be less than 37 days from expiration
                # 3. Must be at least 7 days between near-term and next-term expiration
                # 4. Hard cutoff is less than 120 days from expiration. (My rule, not VIX rule)
                if ((days_to_expiration >= min_near_term_expiration_days) and 
                    (days_to_expiration <= hard_cuttoff_expiration_days) and
                    (expiration not in [e[0] for e in vix_expirations])):
                    
                    if (len(vix_expirations) > 0):
                        last_expiration_days = vix_expirations[-1][1]

                        if (days_to_expiration - last_expiration_days >= 7):
                            vix_expirations.append([expiration, days_to_expiration])    
                            break
                        else:
                            continue

                    vix_expirations.append([expiration, days_to_expiration])

            return {'nearTerm': vix_expirations[0][0], 'nextTerm': vix_expirations[1][0]}
        except:
            raise Exception(
                'This ticker does not have enough option contracts to calculate the VIX Index.',
                sys.exc_info()
            )
        

    
    def __select_near_next_calls_and_puts(self, option_terms: dict, vix_expirations: dict) -> dict:
        """
        Finding the nearest option of each group of options, 
        finding min() value of each group's keys, which are the time to expiration in seconds.
        """

        selected_chain = {}
        for term in ['nearTerm', 'nextTerm']:
            # Selecting the proper calls and puts from option dictionary.
            selected_chain[term] = {
                'call': option_terms['callExpDateMap'][vix_expirations[term]],
                'put': option_terms['putExpDateMap'][vix_expirations[term]],
            }

        return selected_chain


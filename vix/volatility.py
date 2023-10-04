from math import e

class Volatility:
    def calculate(self, f: dict, t: dict, r: float, selected_chain: dict) -> dict:
        """
        f = forward level
        t = time to expiration
        r = risk free rate
        selected_chain = selected option chain
        """

        vol = {}
        for term, options in selected_chain.items():
            min_forward_level = float(int(f[term]))
            k0, ks = self.__calculateK0(options, min_forward_level)

            bounds = self.__calculate_bounds(k0, ks)

            # Collecting put/call averages
            # "Finally, select both the put and call with strike price K0. VIX
            # uses the average of quoted bid and ask, or mid-quote, prices for each option selected. The
            # K0 put and call prices are averaged to produce a single value."
            call_mid_quote = ks['call'][k0]['midquote']
            put_mid_quote = ks['put'][k0]['midquote']
            put_call_avg = (call_mid_quote + put_mid_quote) / 2

            vix_chain = self.__build_vix_chain(bounds, k0, ks, put_call_avg)
            contributions = self.__calculate_strike_contributions(r, t[term], vix_chain)

            # The following is essentially the VIX formula
            # 2/T ∑∆Ki/Ki**2 e**(rt) * q
            sigma_KcT = (2/t[term] * sum(contributions))
            tK = 1/float(t[term]) * pow(((float(f[term]) / float(k0)) - 1), 2)

            v = abs(sigma_KcT - tK)

            vol[term] = v

        return vol

    def __calculateK0(self, options: dict, min_forward_level: float) -> tuple[str, dict]:
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
                if (float(strike) <= min_forward_level):
                    k0 = strike
        return k0, ks

    def __calculate_bounds(self, k0, ks):
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
            strike_list = strikes.keys()
            if (side == 'put'):
                strike_list = list(reversed(strikes.keys()))
            for strike in strike_list:

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

    def __build_vix_chain(self, bounds, k0, ks, put_call_avg):
        """
        Building a new chain excluding all contracts outside of the bounds above.
        """
        vix_chain = []
        for side, strikes in ks.items():
            for strike, data in strikes.items():
                
                if (side == 'call'):
                    if ((strike < k0) or (strike > bounds['call'])): continue
                if (side == 'put'):
                    if ((strike > k0) or (strike < bounds['put'])): continue

                ki = {
                    'side': side,
                    'strike': strike,
                    'bid': data['bid'],
                    'ask': data['ask'],
                    'midquote': data['midquote'],
                }

                # "The K0 put and call prices are averaged to produce a single value"
                if (strike == k0):
                    ki['midquote'] = put_call_avg

                vix_chain.append(ki)

        return vix_chain

    def __calculate_strike_contributions(self, r, t, vix_chain):
        """
        Determining ∆Ki
        "Generally, ∆Ki is half the difference between the strike prices on either side of Ki. For
        example, the ∆K for the next-term 300 Put is 75: ∆K300 Put = (350 – 200)/2. At the upper
        and lower edges of any given strip of options, ∆Ki is simply the difference between Ki and
        the adjacent strike price."
        """

        contributions = []  # Building a list of the "Contribution by Strike"
        vc = sorted(vix_chain, key=lambda i: i['strike'])
        for i, kdata in enumerate(vc):

            strike_above = float(vc[i + 1]['strike']) if (0 <= (i + 1) < len(vc)) else 0
            strike_below = float(vc[i - 1]['strike']) if (0 <= (i - 1) < len(vc)) else 0
            ki = float(kdata['strike'])
            q = float(kdata['midquote'])

            if (i == 0):
                deltaK = strike_above - ki
            elif (i == (len(vc) - 1)):  # Workaround to odd issue with len() after using sorted.
                deltaK = ki - strike_below
            else:
                deltaK = ((strike_above - strike_below) / 2)

            # ∆Ki/Ki**2 e**(rt) * q
            kc = deltaK/pow(ki, 2) * pow(e, r*t) * q

            contributions.append(kc)

        return contributions

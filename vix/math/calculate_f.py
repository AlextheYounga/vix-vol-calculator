from math import e

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
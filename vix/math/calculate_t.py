import datetime
from pytz import timezone

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
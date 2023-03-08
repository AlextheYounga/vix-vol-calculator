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
from vix.vix import vix
from vix.http.fred import scrape_vix_from_fred
from time import sleep

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


def test_vix():
    sleep(1)  # Giving TD API a break
    vix_vol = vix('$SPX.X')
    print(vix_vol)
    assert (type(vix_vol) == float)


def test_accuracy():
    # I have noticed this has become slightly less accurate over time.
    # I am going to go through the math again and see if anything has changed.
    # I can get within 4 points, but that's not good enough.

    sleep(1)  # Giving TD API a break
    actual_SPX_VIX = scrape_vix_from_fred()
    vix_vol = vix('$SPX.X')

    assert (vix_vol - actual_SPX_VIX < abs(4))

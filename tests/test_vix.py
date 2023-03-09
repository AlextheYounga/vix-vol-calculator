from vix.vix import vix
from vix.http.fred import scrape_vix_from_fred
from time import sleep


# def test_vix():
#     sleep(1)  # Giving TD API a break
#     vix_vol = vix('$SPX.X')
#     print(vix_vol)
#     assert (type(vix_vol) == float)


def test_accuracy():
    # I have noticed this has become slightly less accurate over time.
    # I am going to go through the math again and see if anything has changed.
    # I can get within 4 points, but that's not good enough.

    sleep(1)  # Giving TD API a break
    actual_SPX_VIX = scrape_vix_from_fred()
    vix_vol = vix('__TEST__')

    print(f"Vix Calculation: {vix_vol} Actual: {actual_SPX_VIX}")
    assert (vix_vol - actual_SPX_VIX < abs(5))

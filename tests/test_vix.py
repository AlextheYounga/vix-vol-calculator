from vix.vix import Vix
from vix.http.fred import Fred
from time import sleep


def test_accuracy():
    sleep(1)  # Giving TD API a break
    fred = Fred()
    actual_SPX_VIX = fred.scrape_vix()
    vixvol = Vix(debug=True)
    vix = vixvol.calculate('__TEST__')

    print(f"Vix Calculation: {vix} Actual: {actual_SPX_VIX}")
    assert (vix - actual_SPX_VIX < abs(5))

from vix.http.td_ameritrade import TDAmeritrade
from vix.options.options import build_option_chain_time_range
import json

UPDATE_SAMPLE = False

def _save_response_as_example(chain):
    path = 'tests/sample_response/sample_td_response.json'
    with open(path, 'w') as json_file:
        json.dump(chain, json_file)

def test_td_ameritrade_api():
    td = TDAmeritrade()
    time_range = build_option_chain_time_range()
    chain = td.get_option_chain('$SPX.X', time_range)

    if (chain and UPDATE_SAMPLE):
        _save_response_as_example(chain) 

    assert (type(chain) == dict)


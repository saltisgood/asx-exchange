from datetime import datetime
from decimal import Decimal
from io import StringIO

from asx_exchange.market_data.csv_parser import parse_end_of_day_csv
from paper_trader.market_data.types import EndOfDay
from paper_trader.utils.price import Price

TEST_CSV = """Date,Symbol,Open,High,Low,Close,Volume
20110211,CXO,0.23,0.24,0.205,0.21,1010500
20110214,CXO,0.22,0.23,0.21,0.23,290000
20110215,CXO,0.24,0.25,0.23,0.24,223500
20110216,CXO,0.235,0.235,0.215,0.215,188578
20110217,CXO,0.22,0.22,0.215,0.22,130000
20110218,CXO,0.23,0.23,0.215,0.215,314652
20110221,CXO,0.215,0.215,0.215,0.215,0
20110222,CXO,0.215,0.22,0.215,0.22,33709
20110223,CXO,0.22,0.22,0.22,0.22,0
"""

EXPECTED_EODS = [
    EndOfDay('CXO', datetime(2011, 2, 11), '', Price('0.205'), Price('0.24'), Price('0.23'), Price('0.21'), Price('0.0'), Decimal('0.0'), 1010500, Price('212205')),
    EndOfDay('CXO', datetime(2011, 2, 14), '', Price('0.21'), Price('0.23'), Price('0.22'), Price('0.23'), Price('0.02'), Decimal('0.0952'), 290000, Price('66700')),
    EndOfDay('CXO', datetime(2011, 2, 15), '', Price('0.23'), Price('0.25'), Price('0.24'), Price('0.24'), Price('0.01'), Decimal('0.0435'), 223500, Price('53640')),
    EndOfDay('CXO', datetime(2011, 2, 16), '', Price('0.215'), Price('0.235'), Price('0.235'), Price('0.215'), Price('-0.025'), Decimal('-0.1042'), 188578, Price('40544.27')),
    EndOfDay('CXO', datetime(2011, 2, 17), '', Price('0.215'), Price('0.22'), Price('0.22'), Price('0.22'), Price('0.005'), Decimal('0.0233'), 130000, Price('28600')),
    EndOfDay('CXO', datetime(2011, 2, 18), '', Price('0.215'), Price('0.23'), Price('0.23'), Price('0.215'), Price('-0.005'), Decimal('-0.0227'), 314652, Price('67650.18')),
    EndOfDay('CXO', datetime(2011, 2, 21), '', Price('0.215'), Price('0.215'), Price('0.215'), Price('0.215'), Price('0.0'), Decimal('0.0'), 0, Price('0')),
    EndOfDay('CXO', datetime(2011, 2, 22), '', Price('0.215'), Price('0.22'), Price('0.215'), Price('0.22'), Price('0.005'), Decimal('0.0233'), 33709, Price('7415.98')),
    EndOfDay('CXO', datetime(2011, 2, 23), '', Price('0.22'), Price('0.22'), Price('0.22'), Price('0.22'), Price('0.0'), Decimal('0.0'), 0, Price('0'))
]

def test_parse_eod():
    sio = StringIO(TEST_CSV)
    eods = parse_end_of_day_csv(sio)
    assert eods == EXPECTED_EODS

    
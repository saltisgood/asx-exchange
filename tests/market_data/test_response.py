from datetime import date
from decimal import Decimal
from asx_exchange.market_data.response import HistoryResponse
from paper_trader.market_data.types import EndOfDay
from paper_trader.utils.price import Price

HISTORY_RESPONSE = {
    'symbol': 'flt.asx',
    'realSymbol': 'flt.asx',
    'units': 'PRICE',
    'currency': 'AUD',
    'tz': 'AEDT',
    'tickTable': '0.0005<0.1,0.0025<2,0.005',
    'ticks': {
        'totalCount': 10,
        'low': [
            35.971992,
            35.19782,
            35.125804,
            34.171592,
            34.83774,
            35.832461,
            36.332072,
            35.251832,
            34.02756,
            33.338907
        ],
        'minDate': '1995-12-01',
        'open': [
            36.14303,
            36.09802,
            35.125804,
            34.540674,
            34.83774,
            36.071014,
            36.494108,
            36.701154,
            34.900754,
            33.93754,
        ],
        'close': [
            36.14303,
            35.24283,
            35.386862,
            34.74772,
            35.82796,
            36.422092,
            36.656144,
            35.78295,
            34.02756,
            33.7575,
        ],
        'prevClose': [
            35.791952,
            36.14303,
            35.24283,
            35.386862,
            34.74772,
            35.82796,
            36.422092,
            36.656144,
            35.78295,
            34.02756,
        ],
        'value': [
            14487110.85,
            24047920.935,
            36121929.945,
            16872393.36,
            20208693.26,
            25510912.065,
            13730679.845,
            27291296.11,
            30454328.41,
            25606544.18,
        ],
        'date': [
            "2020-01-29",
            "2020-01-30",
            "2020-01-31",
            "2020-02-03",
            "2020-02-04",
            "2020-02-05",
            "2020-02-06",
            "2020-02-07",
            "2020-02-10",
            "2020-02-11"
        ],
        'volume': [
            400228,
            676036,
            999283,
            486775,
            566474,
            702930,
            374569,
            762383,
            887595,
            759214,
        ],
        'high': [
            36.647142,
            36.269058,
            36.080016,
            34.918758,
            36.080016,
            36.422092,
            36.935206,
            36.746164,
            35.350854,
            34.02756,
        ]
    }
}

EXPECTED_HISTORY = [
    EndOfDay('flt', date(2020, 1, 29), 'AUD', Price('35.9720'), Price('36.6471'), Price('36.143'), Price('36.143'), Price('0.351'), Decimal('0.981'), 400228, Price('14487110.85')),
    EndOfDay('flt', date(2020, 1, 30), 'AUD', Price('35.1978'), Price('36.2691'), Price('36.098'), Price('35.2428'), Price('-0.9002'), Decimal('-2.491'), 676036, Price('24047920.935')),
    EndOfDay('flt', date(2020, 1, 31), 'AUD', Price('35.1258'), Price('36.08'), Price('35.1258'), Price('35.3869'), Price('0.1441'), Decimal('0.409'), 999283, Price('36121929.945')),
    EndOfDay('flt', date(2020, 2, 3), 'AUD', Price('34.1716'), Price('34.9188'), Price('34.5407'), Price('34.7477'), Price('-0.6392'), Decimal('-1.806'), 486775, Price('16872393.36')),
    EndOfDay('flt', date(2020, 2, 4), 'AUD', Price('34.8377'), Price('36.08'), Price('34.8377'), Price('35.828'), Price('1.0803'), Decimal('3.109'), 566474, Price('20208693.26')),
    EndOfDay('flt', date(2020, 2, 5), 'AUD', Price('35.8325'), Price('36.4221'), Price('36.071'), Price('36.4221'), Price('0.5941'), Decimal('1.658'), 702930, Price('25510912.065')),
    EndOfDay('flt', date(2020, 2, 6), 'AUD', Price('36.3321'), Price('36.9352'), Price('36.4941'), Price('36.6561'), Price('0.234'), Decimal('0.642'), 374569, Price('13730679.845')),
    EndOfDay('flt', date(2020, 2, 7), 'AUD', Price('35.2518'), Price('36.7462'), Price('36.7012'), Price('35.7829'), Price('-0.8732'), Decimal('-2.382'), 762383, Price('27291296.11')),
    EndOfDay('flt', date(2020, 2, 10), 'AUD', Price('34.0276'), Price('35.3509'), Price('34.9008'), Price('34.0276'), Price('-1.7553'), Decimal('-4.905'), 887595, Price('30454328.41')),
    EndOfDay('flt', date(2020, 2, 11), 'AUD', Price('33.3389'), Price('34.0276'), Price('33.9375'), Price('33.7575'), Price('-0.2701'), Decimal('-0.794'), 759214, Price('25606544.18'))
]

def test_history_response():
    parsed = HistoryResponse.parse(HISTORY_RESPONSE)
    assert parsed == EXPECTED_HISTORY
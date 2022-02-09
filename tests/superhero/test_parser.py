from datetime import datetime
from decimal import Decimal
from dis import Instruction
from paper_trader.utils.price import Price

from asx_exchange.superhero.parser import parse_holdings, parse_orders, parse_security_info, parse_security_performance
from asx_exchange.superhero.types import Holding, Holdings, Order, OrderStatus, Portfolio, PricingInstruction, SecurityInfo, SecurityPriceTime, Side, TradingStatus

# NOTE:
# This is cut down which is why the totals don't add up
EXAMPLE_HOLDINGS = [
    {
        "name": "AUS Portfolio",
        "icon_url": "https://images.superhero.com.au/icons/aus.svg",
        "holdings": [
            {
                "holding_type": "share",
                "portfolio_id": 278,
                "security_id": 16,
                "name": "Argosy Minerals",
                "display_name": "Argosy Minerals",
                "security_code": "AGY.AU",
                "fund_manager": "",
                "logo_url": "https://images.superhero.com.au/logos/agy.png",
                "current_value": 9999.825,
                "gain_loss_value": 72.46,
                "gain_loss_percentage": 0.73,
                "percent_movement_day": 2.99,
                "average_cost_price": 0.3425,
                "last_price": 0.345,
                "units": 28985,
                "has_news": True,
                "trading_status": "Closed",
                "updated_at": 1630013455
            },
            {
                "holding_type": "share",
                "portfolio_id": 278,
                "security_id": 1047,
                "name": "Chalice Mining",
                "display_name": "Chalice Mining",
                "security_code": "CHN.AU",
                "fund_manager": None,
                "logo_url": "https://images.superhero.com.au/logos/chn.png",
                "current_value": 9932.94,
                "gain_loss_value": -62.55,
                "gain_loss_percentage": -0.63,
                "percent_movement_day": 2.85,
                "average_cost_price": 7.99,
                "last_price": 7.94,
                "units": 1251,
                "has_news": False,
                "trading_status": "Closed",
                "updated_at": 1639090949
            }
        ],
        "total_current_value": 39782.1,
        "total_gain_loss_value": -140.088,
        "total_gain_loss_percentage": -0.35
    },
    {
        "name": "US Portfolio",
        "icon_url": "https://images.superhero.com.au/icons/us.svg",
        "holdings": [],
        "total_current_value": 0,
        "total_gain_loss_value": 0,
        "total_gain_loss_percentage": 0
    }
]

EXPECTED_HOLDINGS = Holdings(
    aus=Portfolio(
        name='AUS Portfolio',
        holdings=[
            Holding(
                portfolio_id=278,
                security_id=16,
                name="Argosy Minerals",
                display_name="Argosy Minerals",
                security_code="AGY.AU",
                percent_movement_day=Decimal("2.99"),
                last_price=Price("0.345"),
                has_news=True,
                trading_status=TradingStatus.CLOSED,
                current_value=Price("9999.825"),
                gain_loss_value=Price("72.46"),
                gain_loss_percentage=Decimal("0.73"),
                average_cost_price=Price("0.3425"),
                units=28985
            ),
            Holding(
                portfolio_id=278,
                security_id=1047,
                name="Chalice Mining",
                display_name="Chalice Mining",
                security_code="CHN.AU",
                percent_movement_day=Decimal("2.85"),
                last_price=Price("7.94"),
                has_news=False,
                trading_status=TradingStatus.CLOSED,
                current_value=Price("9932.94"),
                gain_loss_value=Price("-62.55"),
                gain_loss_percentage=Decimal("-0.63"),
                average_cost_price=Price("7.99"),
                units=1251
            ),
        ],
        total_current_value=Price("39782.1"),
        total_gain_loss_value=Price("-140.088"),
        total_gain_loss_percentage=Decimal("-0.35")
    ),
    us=Portfolio(
        name="US Portfolio",
        holdings=[],
        total_current_value=Price("0.0"),
        total_gain_loss_value=Price("0.0"),
        total_gain_loss_percentage=Decimal("0.0")
    )
)

def test_parse_holdings():
    assert EXPECTED_HOLDINGS == parse_holdings(EXAMPLE_HOLDINGS)

EXAMPLE_SECURITY_INFO = {
    "allow_fractional_units": False,
    "code": "AGY.AU",
    "company_profile": {
        "long_description": "Argosy Minerals Limited engages in the acquisition and development of lithium exploration projects in Australia and the United States. It primarily holds a 77.5% interest in the Rincon lithium project that covers an area of approximately 2,794 hectares of mining concessions located within the Salar del Rincon in Salta Province, Argentina; and 100% interest in the Tonopah lithium project comprises 425 claims covering an area of approximately 34.25 square kilometers located in the Big Smokey Valley region in Nevada, the United States. The company was incorporated in 2010 and is headquartered in Perth, Australia.",
        "sector": "Materials",
        "short_description": None,
        "subsector": "Materials"
    },
    "currency": {
        "code": "AUD",
        "icon_url": "https://images.superhero.com.au/icons/aus.svg"
    },
    "display_name": "Argosy Minerals",
    "earn_qff_points": True,
    "exchange": "ASX",
    "fact_sheet": "",
    "fund_manager": "",
    "gain_loss_percentage": 0.73,
    "gain_loss_value": 72.46,
    "has_news": True,
    "holding": 28985,
    "image_url": "",
    "is_following": True,
    "is_invested": True,
    "logo_url": "https://images.superhero.com.au/logos/agy.png",
    "market": {
        "code": "AU",
        "icon_url": "https://images.superhero.com.au/icons/aus.svg"
    },
    "maximum_buy_value": 3937.07,
    "maximum_sell_units": 28985,
    "name": "Argosy Minerals",
    "pending_sell_units": 0,
    "pricing_instruction": {
        "limit": {
            "buy": "whole",
            "sell": "whole"
        },
        "market_to_limit": {
            "buy": "whole",
            "sell": "whole"
        }
    },
    "quote": {
        "ask_price": 0.35,
        "ask_volume": 135661,
        "bid_price": 0.345,
        "bid_volume": 129571,
        "buyers_price": 0.345,
        "dividend_yield": 0,
        "high_price": 0.365,
        "indicative_price": {
            "buy": None,
            "sell": None, 
        },
        "last_price": 0.345,
        "low_price": 0.34,
        "match_price": 0,
        "match_volume": "0.00000",
        "open_price": 0.36,
        "previous_close_price": 0.335,
        "sellers_price": 0.35,
        "volume": 17884748
    },
    "security_code": "AGY.AU",
    "security_id": 16,
    "security_information": {
        "earnings_per_share": -0.0015,
        "market_capitalisation": 431314428,
        "pe_ratio": -230
    },
    "security_type": "share",
    "trade_history": {
        "high_year_price": 0.455,
        "low_year_price": 0.084,
        "market_vwap": 0.353,
        "percent_movement_day": 2.99,
        "percent_movement_year": 102.94,
        "price_movement_day": 100
    },
    "trading_status": "Closed"
}

EXPECTED_SECURITY_INFO = SecurityInfo(
    security_id=16,
    attributes=SecurityInfo.Attributes(
        name="Argosy Minerals",
        display_name="Argosy Minerals",
        security_code="AGY.AU",
        exchange="ASX",
        has_news=True,
        trading_status=TradingStatus.CLOSED,
        sector="Materials",
        subsector="Materials",
        description=EXAMPLE_SECURITY_INFO["company_profile"]["long_description"]
    ),
    user=SecurityInfo.User(
        holding=28985,
        maximum_buy_value=Price('3937.07'),
        maximum_sell_units=28985,
        gain_loss_value=Price('72.46'),
        gain_loss_percentage=Decimal('0.73')
    ),
    quote=SecurityInfo.Quote(
        last_price=Price('0.345'),
        open_price=Price('0.36'),
        low_price=Price('0.34'),
        high_price=Price('0.365'),
        previous_close_price=Price('0.335'),
        match_price=Price('0'),
        match_volume=Decimal('0.0'),
        volume=17884748,
        bid_volume=129571,
        ask_volume=135661,
        bid_price=Price('0.345'),
        ask_price=Price('0.35'),
        buyers_price=Price('0.345'),
        sellers_price=Price('0.35')
    ),
    history=SecurityInfo.History(
        low_year_price=Price('0.084'),
        high_year_price=Price('0.455'),
        percent_movement_day=Decimal('2.99'),
        percent_movement_year=Decimal('102.94'),
        market_vwap=Price('0.353')
    )
)

def test_parse_security_info():
    assert EXPECTED_SECURITY_INFO == parse_security_info(EXAMPLE_SECURITY_INFO)

EXAMPLE_PERFORMANCE_1D = [
    {
        "close_price": 0.365,
        "high_price": 36.5,
        "low_price": 35.5,
        "open_price": 0,
        "percent_movement": 8.96,
        "time_series_date": 1643670060
    },
    {
        "close_price": 0.365,
        "high_price": 36.5,
        "low_price": 35.5,
        "open_price": 0,
        "percent_movement": 8.96,
        "time_series_date": 1643670120
    },
    {
        "close_price": 0.365,
        "high_price": 36.5,
        "low_price": 35.5,
        "open_price": 0,
        "percent_movement": 8.96,
        "time_series_date": 1643670240
    },
    {
        "close_price": 0.36,
        "high_price": 36.5,
        "low_price": 35.5,
        "open_price": 0,
        "percent_movement": 7.46,
        "time_series_date": 1643670300
    },
    {
        "close_price": 0.363,
        "high_price": 36.5,
        "low_price": 35.5,
        "open_price": 0,
        "percent_movement": 8.36,
        "time_series_date": 1643670360
    },
]

# NOTE:
# The times are 1m/2m apart
# The open price is always 0.0
# The low price is wrong
# The high price is wrong
# The close price is the value that's used
# The percent movement is relative to yesterday's close
EXPECTED_PERFORMANCE_1D = [
    SecurityPriceTime(
        time=datetime(2022, 2, 1, 10, 1),
        open_price=Price('0.0'),
        close_price=Price('0.365'),
        low_price=Price('35.5'),
        high_price=Price('36.5'),
        percent_movement=Decimal('8.960')
    ),
    SecurityPriceTime(
        time=datetime(2022, 2, 1, 10, 2),
        open_price=Price('0.0'),
        close_price=Price('0.365'),
        low_price=Price('35.5'),
        high_price=Price('36.5'),
        percent_movement=Decimal('8.960')
    ),
    SecurityPriceTime(
        time=datetime(2022, 2, 1, 10, 4),
        open_price=Price('0.0'),
        close_price=Price('0.365'),
        low_price=Price('35.5'),
        high_price=Price('36.5'),
        percent_movement=Decimal('8.960')
    ),
    SecurityPriceTime(
        time=datetime(2022, 2, 1, 10, 5),
        open_price=Price('0.0'),
        close_price=Price('0.36'),
        low_price=Price('35.5'),
        high_price=Price('36.5'),
        percent_movement=Decimal('7.460')
    ),
    SecurityPriceTime(
        time=datetime(2022, 2, 1, 10, 6),
        open_price=Price('0.0'),
        close_price=Price('0.363'),
        low_price=Price('35.5'),
        high_price=Price('36.5'),
        percent_movement=Decimal('8.360')
    ),
]

def test_parse_security_performance_1d():
    assert EXPECTED_PERFORMANCE_1D == parse_security_performance(EXAMPLE_PERFORMANCE_1D)

# NOTE:
# Compared to the 1d
# Time deltas are 30min
# All the prices work now
EXAMPLE_PERFORMANCE_5D = [
    {
        "time_series_date": 1643065200,
        "close_price": 0.34,
        "open_price": 0.34,
        "high_price": 0.35,
        "low_price": 0.34,
        "percent_movement": 0
    },
    {
        "time_series_date": 1643067000,
        "close_price": 0.34,
        "open_price": 0.345,
        "high_price": 0.345,
        "low_price": 0.34,
        "percent_movement": 0
    },
    {
        "time_series_date": 1643068800,
        "close_price": 0.328,
        "open_price": 0.34,
        "high_price": 0.34,
        "low_price": 0.325,
        "percent_movement": -3.53
    },
    {
        "time_series_date": 1643070600,
        "close_price": 0.32,
        "open_price": 0.328,
        "high_price": 0.328,
        "low_price": 0.32,
        "percent_movement": -5.88
    },
    {
        "time_series_date": 1643072400,
        "close_price": 0.315,
        "open_price": 0.32,
        "high_price":0.32,
        "low_price":0.31,
        "percent_movement":-7.35
    },
    {
        "time_series_date": 1643074200,
        "close_price": 0.32,
        "open_price": 0.32,
        "high_price": 0.325,
        "low_price": 0.315,
        "percent_movement": -5.88
    },
]

EXPECTED_PERFORMANCE_5D = [
    SecurityPriceTime(
        time=datetime(2022, 1, 25, 10),
        open_price=Price('0.34'),
        close_price=Price('0.34'),
        low_price=Price('0.34'),
        high_price=Price('0.35'),
        percent_movement=Decimal('0.0')
    ),
    SecurityPriceTime(
        time=datetime(2022, 1, 25, 10, 30),
        open_price=Price('0.345'),
        close_price=Price('0.34'),
        low_price=Price('0.34'),
        high_price=Price('0.345'),
        percent_movement=Decimal('0.0')
    ),
    SecurityPriceTime(
        time=datetime(2022, 1, 25, 11),
        open_price=Price('0.34'),
        close_price=Price('0.328'),
        low_price=Price('0.325'),
        high_price=Price('0.34'),
        percent_movement=Decimal('-3.53')
    ),
    SecurityPriceTime(
        time=datetime(2022, 1, 25, 11, 30),
        open_price=Price('0.328'),
        close_price=Price('0.32'),
        low_price=Price('0.32'),
        high_price=Price('0.328'),
        percent_movement=Decimal('-5.88')
    ),
    SecurityPriceTime(
        time=datetime(2022, 1, 25, 12),
        open_price=Price('0.32'),
        close_price=Price('0.315'),
        low_price=Price('0.31'),
        high_price=Price('0.32'),
        percent_movement=Decimal('-7.35')
    ),
    SecurityPriceTime(
        time=datetime(2022, 1, 25, 12, 30),
        open_price=Price('0.32'),
        close_price=Price('0.32'),
        low_price=Price('0.315'),
        high_price=Price('0.325'),
        percent_movement=Decimal('-5.88')
    ),
]

def test_parse_security_performance_5d():
    assert EXPECTED_PERFORMANCE_5D == parse_security_performance(EXAMPLE_PERFORMANCE_5D)

EXAMPLE_ORDERS = [
      {
            "pending_type": "order",
            "order_id": 17928,
            "security_id": 1926,
            "name": "Renascor Resources",
            "display_name": "Renascor Resources",
            "security_code": "RNU.AU",
            "fund_manager": "",
            "logo_url": "https://images.superhero.com.au/icons/activity/sell.svg",
            "currency": {
                "code": "AUD",
                "icon_url": "https://images.superhero.com.au/icons/aus.svg"
            },
            "last_price": 0.325,
            "order_type": "Sell",
            "order_price": 0.355,
            "order_volume": 28571,
            "order_volume_outstanding": 28570,
            "amount_to_invest": None,
            "brokerage_fee": 5,
            "order_total": 10137.7,
            "pricing_instruction": "Limit",
            "status": "PENDING",
            "can_cancel": True,
            "has_link": True,
            "created_at": 1644371128,
            "updated_at": 1644371133,
            "member_notes": None
        },
        {
            "pending_type": "order",
            "order_id": 1787,
            "security_id": 273,
            "name": "Mineral Resources",
            "display_name": "Mineral Resources",
            "security_code": "MIN.AU",
            "fund_manager": "",
            "logo_url": "https://images.superhero.com.au/icons/activity/sell.svg",
            "currency": {
                "code": "AUD",
                "icon_url": "https://images.superhero.com.au/icons/aus.svg"
            },
            "last_price": 52.72,
            "order_type": "Sell",
            "order_price": 60,
            "order_volume": 238,
            "order_volume_outstanding": 238,
            "amount_to_invest": None,
            "brokerage_fee": 5,
            "order_total": 14275,
            "pricing_instruction": "Limit",
            "status": "CANCELLED",
            "can_cancel": True,
            "has_link": True,
            "created_at": 1644296104,
            "updated_at": 1644296107,
            "member_notes": None
        },
        {
            "pending_type": "order",
            "order_id": 123456,
            "security_id": 7307,
            "name": "Pacgold",
            "display_name": "Pacgold",
            "security_code": "PGO.AU",
            "fund_manager": None,
            "logo_url": "https://images.superhero.com.au/icons/activity/sell.svg",
            "currency": {
                "code": "AUD",
                "icon_url": "https://images.superhero.com.au/icons/aus.svg"
            },
            "last_price": 0.95,
            "order_type": "Sell",
            "order_price": 1.01,
            "order_volume": 10000,
            "order_volume_outstanding": 10000,
            "amount_to_invest": None,
            "brokerage_fee": 5,
            "order_total": 10095,
            "pricing_instruction": "Limit",
            "status": "PENDING",
            "can_cancel": True,
            "has_link": True,
            "created_at": 1644296018,
            "updated_at": 1644296022,
            "member_notes": None
        },
]

EXPECTED_ORDERS = [
    Order(
        order_id=17928,
        status=OrderStatus.PENDING,
        price=Price('0.355'),
        quantity=28571,
        quantity_outstanding=28570,
        side=Side.SELL,
        instruction=PricingInstruction.LIMIT,
        can_cancel=True,
        total=Price('10137.7'),
        security=Order.Security(
            security_id=1926,
            name='Renascor Resources',
            display_name='Renascor Resources',
            security_code='RNU.AU',
            last_price=Price('0.325')
        )
    ),
    Order(
        order_id=1787,
        status=OrderStatus.CANCELLED,
        price=Price('60'),
        quantity=238,
        quantity_outstanding=238,
        side=Side.SELL,
        instruction=PricingInstruction.LIMIT,
        can_cancel=True,
        total=Price('14275'),
        security=Order.Security(
            security_id=273,
            name='Mineral Resources',
            display_name='Mineral Resources',
            security_code='MIN.AU',
            last_price=Price('52.72')
        )
    ),
    Order(
        order_id=123456,
        status=OrderStatus.PENDING,
        price=Price('1.01'),
        quantity=10000,
        quantity_outstanding=10000,
        side=Side.SELL,
        instruction=PricingInstruction.LIMIT,
        can_cancel=True,
        total=Price('10095'),
        security=Order.Security(
            security_id=7307,
            name='Pacgold',
            display_name='Pacgold',
            security_code='PGO.AU',
            last_price=Price('0.95')
        )
    )
]

def test_parse_orders():
    assert EXPECTED_ORDERS == parse_orders(EXAMPLE_ORDERS)
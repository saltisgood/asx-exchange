from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto, unique

from paper_trader.utils.dataclasses import primary_key
from paper_trader.utils.price import Price

@unique
class HoldingType(Enum):
    UNKNOWN = auto()
    SHARE = auto()

    @staticmethod
    def parse(value: str):
        if value.lower() == "share":
            return HoldingType.SHARE
        # TODO: warn
        return HoldingType.UNKNOWN

@unique
class TradingStatus(Enum):
    UNKNOWN = auto()
    CLOSED = auto()
    PREOPEN = auto()

    @staticmethod
    def parse(value: str):
        if value.lower() == "closed":
            return TradingStatus.CLOSED
        elif value.lower() == "pre-open":
            return TradingStatus.PREOPEN
        # TODO: warn
        return HoldingType.UNKNOWN


@unique
class Side(Enum):
    UNKNOWN = auto()
    BUY = auto()
    SELL = auto()

    @staticmethod
    def parse(value: str):
        if value.lower() == "buy":
            return Side.BUY
        elif value.lower() == "sell":
            return Side.SELL
        return Side.UNKNOWN

    def __str__(self):
        return "Buy" if self == Side.BUY else "Sell"

@unique
class PricingInstruction(Enum):
    UNKNOWN = auto()
    MARKET_TO_LIMIT = auto()
    LIMIT = auto()

    @staticmethod
    def parse(value: str):
        if value.lower() == "markettolimit":
            return PricingInstruction.MARKET_TO_LIMIT
        elif value.lower() == "limit":
            return PricingInstruction.LIMIT
        return PricingInstruction.UNKNOWN

    def __str__(self):
        if self == PricingInstruction.MARKET_TO_LIMIT:
            return "MarketToLimit"
        elif self == PricingInstruction.LIMIT:
            return "Limit"
        return ""

@unique
class OrderStatus(Enum):
    UNKNOWN = auto()
    PENDING = auto()
    CANCELLED = auto()
    # Special value: Is not a valid value other than as a sentry
    ALL = auto()

    @staticmethod
    def parse(value: str):
        if value.lower() == "pending":
            return OrderStatus.PENDING
        elif value.lower() == "cancelled":
            return OrderStatus.CANCELLED
        elif value.lower() == "all":
            # Not symmetric because it's a sentry
            return OrderStatus.ALL
        return OrderStatus.UNKNOWN 

    def __str__(self):
        if self == OrderStatus.PENDING:
            return "PENDING"
        elif self == OrderStatus.CANCELLED:
            return "CANCELLED"
        elif self == OrderStatus.ALL:
            return ""
        raise RuntimeError("Unknown OrderStatus value: " + repr(self))


@dataclass(frozen=True)
class Holding:
    # Portfolio
    portfolio_id: int

    # Security
    security_id: int
    name: str
    display_name: str
    security_code: str
    percent_movement_day: Decimal
    last_price: Price
    has_news: bool
    trading_status: TradingStatus

    # User
    current_value: Price
    gain_loss_value: Price
    gain_loss_percentage: Decimal
    average_cost_price: Price
    units: int

@dataclass(frozen=True)
class Portfolio:
    name: str
    holdings: list[Holding]
    total_current_value: Price
    total_gain_loss_value: Price
    total_gain_loss_percentage: Decimal

@dataclass(frozen=True)
class Holdings:
    aus: Portfolio
    us: Portfolio

@dataclass(frozen=True)
@primary_key('security_id')
class SecurityInfo:
    security_id: int

    @dataclass(frozen=True)
    class Attributes:
        name: str
        display_name: str
        security_code: str
        exchange: str
        has_news: bool
        trading_status: TradingStatus
        sector: str
        subsector: str
        description: str
    attributes: Attributes

    @dataclass(frozen=True)
    class User:
        holding: int
        maximum_buy_value: Price
        maximum_sell_units: int
        gain_loss_value: Price
        gain_loss_percentage: Decimal
    user: User

    @dataclass(frozen=True)
    class Quote:
        last_price: Price
        open_price: Price
        low_price: Price
        high_price: Price
        previous_close_price: Price
        match_price: Price
        match_volume: Decimal
        volume: int
        bid_volume: int
        ask_volume: int
        bid_price: Price
        ask_price: Price
        buyers_price: Price
        sellers_price: Price
    quote: Quote

    @dataclass(frozen=True)
    class History:
        low_year_price: Price
        high_year_price: Price
        percent_movement_day: Decimal
        percent_movement_year: Decimal
        market_vwap: Price
    history: History

@dataclass(frozen=True)
@primary_key('time')
class SecurityPriceTime:
    time: datetime

    # Prices:
    # NOTE: For the 1d performance, only the close_price is accurate
    open_price: Price
    close_price: Price
    low_price: Price
    high_price: Price

    # The percent movement relative to the time period
    # For 1d: change compared to yesterday's close
    # For 5d: change compared to start of the 5d
    percent_movement: Decimal

SecurityPriceTimes = list[SecurityPriceTime]

@dataclass(frozen=True)
class MarketDepth:
    @dataclass(frozen=True)
    class Level:
        price: Price
        volume: int
        count: int
    
    bids: list[Level] = field(default_factory=list[Level])
    asks: list[Level] = field(default_factory=list[Level])

@dataclass(frozen=True)
class Order:
    order_id: int
    status: OrderStatus
    price: Price
    quantity: int
    quantity_outstanding: int
    side: Side
    instruction: PricingInstruction
    can_cancel: bool
    total: Price

    @dataclass(frozen=True)
    class Security:
        security_id: int
        name: str
        display_name: str
        security_code: str
        last_price: Price

    security: Security

Orders = list[Order]
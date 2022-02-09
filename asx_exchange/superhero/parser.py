from datetime import datetime
from decimal import Decimal

from paper_trader.utils.price import Price

from .types import Holding, Holdings, MarketDepth, Order, OrderStatus, Orders, Portfolio, PricingInstruction, SecurityInfo, SecurityPriceTime, SecurityPriceTimes, Side, TradingStatus

PCT_QUANTIZED = Decimal('0.001')

def _parse_percent(value: float):
    return Decimal(value).quantize(PCT_QUANTIZED)

def parse_holding(data: dict):
    return Holding(
        portfolio_id=data['portfolio_id'],
        security_id=data['security_id'],
        name=data['name'],
        display_name=data['display_name'],
        security_code=data['security_code'],
        percent_movement_day=_parse_percent(data['percent_movement_day']),
        last_price=Price(data['last_price']),
        has_news=data['has_news'],
        trading_status=TradingStatus.parse(data['trading_status']),
        current_value=Price(data['current_value']),
        gain_loss_value=Price(data['gain_loss_value']),
        gain_loss_percentage=_parse_percent(data['gain_loss_percentage']),
        average_cost_price=Price(data['average_cost_price']),
        units=data['units']
    )

def parse_portfolio(data: dict):
    portfolio = Portfolio(
        name=data['name'],
        holdings=list[Holding](),
        total_current_value=Price(data['total_current_value']),
        total_gain_loss_value=Price(data['total_gain_loss_value']),
        total_gain_loss_percentage=_parse_percent(data['total_gain_loss_percentage'])
    )

    for holding in data['holdings']:
        portfolio.holdings.append(parse_holding(holding))
    
    return portfolio

def parse_holdings(data: list):
    portfolios = [parse_portfolio(p) for p in data]

    def _first(sequence):
        assert len(sequence) == 1
        return sequence[0]

    aus_portfolio = _first([p for p in portfolios if p.name.startswith('AUS')])
    us_portfolio = _first([p for p in portfolios if p.name.startswith('US')])

    return Holdings(
        aus=aus_portfolio,
        us=us_portfolio
    )

def parse_security_info(data: dict):
    profile = data['company_profile']
    quote = data['quote']
    hist = data['trade_history']

    return SecurityInfo(
        security_id=data['security_id'],
        attributes=SecurityInfo.Attributes(
            name=data['name'],
            display_name=data['display_name'],
            security_code=data['security_code'], # Same as code?
            exchange=data['exchange'],
            has_news=data['has_news'],
            trading_status=TradingStatus.parse(data['trading_status']),
            sector=profile['sector'],
            subsector=profile['subsector'],
            description=profile['long_description']
        ),
        user=SecurityInfo.User(
            holding=data['holding'],
            maximum_buy_value=Price(data['maximum_buy_value']),
            maximum_sell_units=data['maximum_sell_units'],
            gain_loss_value=Price(data['gain_loss_value']),
            gain_loss_percentage=_parse_percent(data['gain_loss_percentage'])
        ),
        quote=SecurityInfo.Quote(
            last_price=Price(quote['last_price']),
            open_price=Price(quote['open_price']),
            low_price=Price(quote['low_price']),
            high_price=Price(quote['high_price']),
            previous_close_price=Price(quote['previous_close_price']),
            match_price=Price(quote['match_price']),
            match_volume=Decimal(quote['match_volume']),
            volume=quote['volume'],
            bid_volume=quote['bid_volume'],
            ask_volume=quote['ask_volume'],
            bid_price=Price(quote['bid_price']),
            ask_price=Price(quote['ask_price']),
            buyers_price=Price(quote['buyers_price']),
            sellers_price=Price(quote['sellers_price'])
        ),
        history=SecurityInfo.History(
            low_year_price=Price(hist['low_year_price']),
            high_year_price=Price(hist['high_year_price']),
            percent_movement_day=_parse_percent(hist['percent_movement_day']),
            percent_movement_year=_parse_percent(hist['percent_movement_year']),
            market_vwap=Price(hist['market_vwap'])
        )
    )

def parse_security_pricetime(data: dict):
    return SecurityPriceTime(
        time=datetime.fromtimestamp(data['time_series_date']),
        open_price=Price(data['open_price']),
        close_price=Price(data['close_price']),
        low_price=Price(data['low_price']),
        high_price=Price(data['high_price']),
        percent_movement=_parse_percent(data['percent_movement'])
    )

def parse_security_performance(data: list):
    return SecurityPriceTimes(parse_security_pricetime(d) for d in data)

def parse_security_depth(data: list):
    depth = MarketDepth()

    for level in data:
        bid = level['bid']
        if bid['price'] is not None:
            depth.bids.append(MarketDepth.Level(Price(bid['price']), bid['volume'], bid['count']))
        
        ask = level['ask']
        if ask['price'] is not None:
            depth.asks.append(MarketDepth.Level(Price(ask['price']), ask['volume'], ask['count']))
    
    return depth

def parse_order(data: dict):
    return Order(
        order_id=data['order_id'],
        status=OrderStatus.parse(data['status']),
        price=Price(data['order_price']),
        quantity=data['order_volume'],
        quantity_outstanding=data['order_volume_outstanding'],
        side=Side.parse(data['order_type']),
        instruction=PricingInstruction.parse(data['pricing_instruction']),
        can_cancel=data['can_cancel'],
        total=Price(data['order_total']),
        security=Order.Security(
            security_id=data['security_id'],
            name=data['name'],
            display_name=data['display_name'],
            security_code=data['security_code'],
            last_price=Price(data['last_price'])
        )
    )

def parse_orders(data: list):
    return Orders(parse_order(d) for d in data)

class MasterParser:
    @staticmethod
    def parse_holdings(data: list):
        return parse_holdings(data)
    
    @staticmethod
    def parse_security_info(data: dict):
        return parse_security_info(data)
    
    @staticmethod
    def parse_security_performance(data: list):
        return parse_security_performance(data)
    
    @staticmethod
    def parse_security_depth(data: list):
        return parse_security_depth(data)

    @staticmethod
    def parse_orders(data: list):
        return parse_orders(data)
from decimal import Decimal
import logging
import math

from paper_trader.utils.price import Price

from asx_exchange.superhero.types import OrderStatus

from ..superhero import ConnectionProto, PricingInstruction, Side

class LastPriceConditionalOrder:
    """
    Watches for the last price to fall below a certain threshold and will
    then send a SELL market order.
    """
    @staticmethod
    def estimate_tick_size(prices: list[Price]):
        factor = Decimal('100000')
        normed_prices = [int(p.value * factor) for p in prices]

        tick_size = math.gcd(*normed_prices)
        return Price(Decimal(tick_size) / factor)

    def __init__(self, conn: ConnectionProto, security_id: int, min_price: Price, sell_volume: int, sell_price: Price):
        self._conn = conn
        self._security_id = security_id
        self._min_price = min_price
        self._sell_volume = sell_volume
        self._sell_price = sell_price
        self._logger = logging.getLogger("asx_exchange.strategy.conditional_order")
        self._name = self._conn.get_security_info(security_id).attributes.display_name
    
    def validate(self):
        depth = self._conn.get_security_depth(self._security_id)
        estimated_tick_size = self.estimate_tick_size([l.price for l in depth.asks] + [l.price for l in depth.bids])
        sec_info = self._conn.get_security_info(self._security_id)
        step_back_ticks = (sec_info.quote.last_price - self._min_price) / estimated_tick_size
        decision = input(f'The cut off price is approx {step_back_ticks} ticks from last price. Is this correct? [Y/n] ')
        if decision != 'Y':
            print("Cancelled")
            return False
        
        sell_back_ticks = (sec_info.quote.last_price - self._sell_price) / estimated_tick_size
        sell_back_from_min_ticks = (self._min_price - self._sell_price) / estimated_tick_size
        decision = input(f'The sell price is approx {sell_back_ticks} ticks from last price and {sell_back_from_min_ticks} ticks from sell price. Is this correct? [Y/n] ')
        if decision != 'Y':
            print("Cancelled")
            return False

        validated, errors = self._conn.validate_order(self._security_id, self._sell_price, self._sell_volume, Side.SELL, PricingInstruction.LIMIT)
        if not validated:
            print(f"Failed to validate possible order: {errors}")
            return False

        return True

    def run(self):
        sec_info = self._conn.get_security_info(self._security_id)
        if sec_info.quote.last_price < self._min_price:
            self._logger.info("%s triggered (last_price=%s)", self, sec_info.quote.last_price)

            # Cancel any active orders on the security so we can fire
            active_orders = self._conn.get_orders(OrderStatus.PENDING)
            for active_order in active_orders:
                if active_order.security.security_id != self._security_id:
                    continue

                self._conn.cancel_order(active_order.order_id)

            # Fire the order
            order_id = self._conn.create_order(self._security_id, self._sell_price, self._sell_volume, Side.SELL, PricingInstruction.LIMIT)
            self._logger.info("%s created order id %d", self, order_id)
            return True
        return False

    def __str__(self):
        return f"LastPriceConditionalOrder({self._name}.last_price < {self._min_price})"

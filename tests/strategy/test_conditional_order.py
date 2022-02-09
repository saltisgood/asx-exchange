from unittest import mock

import pytest

from paper_trader.utils.price import Price

from asx_exchange.strategy import LastPriceConditionalOrder
from asx_exchange.superhero import ConnectionProto
from asx_exchange.superhero.types import OrderStatus, PricingInstruction, Side

def test_estimate_tick_size():
    prices = [Price('5.0'), Price('20.0'), Price('30.0')]
    assert LastPriceConditionalOrder.estimate_tick_size(prices) == Price('5.0')

    prices.append(Price('7.0'))
    assert LastPriceConditionalOrder.estimate_tick_size(prices) == Price('1.0')

    prices.append(Price('3.5'))
    assert LastPriceConditionalOrder.estimate_tick_size(prices) == Price('0.5')

    prices.append(Price('1.25'))
    assert LastPriceConditionalOrder.estimate_tick_size(prices) == Price('0.25')


@pytest.fixture
def conn():
    m = mock.Mock(spec=ConnectionProto)
    class Fake:
        class _1:
            display_name = ''
        attributes = _1()

        class _2:
            last_price = Price('0.40')
        quote = _2()

    m.get_security_info = mock.Mock(return_value=Fake())
    return m

def test_validate(conn):
    class Depth:
        class Level:
            def __init__(self, p):
                self.price = Price(p)
        asks = [Level('0.45'), Level('0.50'), Level('0.55')]
        bids = [Level('0.30'), Level('0.20')]

    conn.get_security_depth = mock.Mock(return_value=Depth())
    co = LastPriceConditionalOrder(conn, 123, Price('0.35'), 456, Price('0.30'))

    with mock.patch('builtins.input', return_value='n'):
        assert not co.validate()
    
    conn.get_security_depth.assert_called_with(123)
    
    conn.validate_order = mock.Mock(return_value=(False, []))
    with mock.patch('builtins.input', return_value='Y'):
        assert not co.validate()
        conn.validate_order.assert_called_with(123, Price('0.30'), 456, Side.SELL, PricingInstruction.LIMIT)
    
    conn.validate_order.return_value = (True, [])
    with mock.patch('builtins.input', return_value='Y'):
        assert co.validate()

def test_run_not_fired(conn):
    co = LastPriceConditionalOrder(conn, 123, Price('0.30'), 1, Price('0.30'))
    conn.get_security_info.reset_mock()
    assert not co.run()
    conn.get_security_info.assert_called_with(123)
    conn.create_order.assert_not_called()

def test_run_fired(conn):
    co = LastPriceConditionalOrder(conn, 123, Price('0.50'), 456, Price('0.45'))

    class Fake:
        class Sec:
            def __init__(self, sec_id):
                self.security_id = sec_id
        
        def __init__(self, sec_id, order_id):
            self.security = Fake.Sec(sec_id)
            self.order_id = order_id

    conn.get_orders = mock.Mock(return_value=[Fake(124, 988), Fake(123, 989)])
    conn.cancel_order = mock.Mock()
    conn.create_order = mock.Mock(return_value=990)
    assert co.run()
    conn.get_orders.assert_called_with(OrderStatus.PENDING)
    conn.cancel_order.assert_called_with(989)
    conn.create_order.assert_called_with(123, Price('0.45'), 456, Side.SELL, PricingInstruction.LIMIT)
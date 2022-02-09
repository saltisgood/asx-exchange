import unittest.mock as mock

import pytest

from paper_trader.utils.price import Price

from asx_exchange.superhero import Connection
from asx_exchange.superhero.parser import MasterParser
from asx_exchange.superhero.types import OrderStatus, PricingInstruction, Side
from asx_exchange.util.secrets import Secrets

@pytest.fixture
def parser():
    return mock.Mock(spec=MasterParser)

@pytest.fixture
def logged_out_conn(parser):
    return Connection(Secrets({
        'superhero': {
            'username': 'myuser',
            'password': 'mypass',
            'pin': 'mypin',
        },
    }), parser=parser)

def test_login(logged_out_conn: Connection, requests_mock):
    requests_mock.post('https://api.superhero.com.au/auth/login', additional_matcher=lambda request: request.json() == {
        "email": "myuser",
        "password": "mypass",
        "g-recaptcha-response": "1",
        "isUsingBioAuth": True
    }, json={
        "data": {
            "content": "a bunch of bullshit"
        },
        "meta": {
            "access_token": "blah di blah"
        }
    })

    assert not logged_out_conn.logged_in
    logged_out_conn.login()
    assert logged_out_conn.logged_in

@pytest.fixture
def conn(logged_out_conn: Connection, requests_mock):
    requests_mock.post('https://api.superhero.com.au/auth/login', status_code=200, json={
        "data": {
            "foo": "a bunch of bullshit"
        },
        "meta": {
            "access_token": "blah di blah"
        }
    })
    logged_out_conn.login()
    return logged_out_conn

def test_refresh_token(conn: Connection, requests_mock):
    requests_mock.get('https://api.superhero.com.au/auth/refresh-token', request_headers={'Authorization': 'Bearer blah di blah'}, status_code=200, json={
        "title": "200 OK",
        "detail": "Token refreshed",
        "data": None,
        "meta": {
            "access_token": "blah di blah 1"
        }
    })
    requests_mock.get('https://api.superhero.com.au/auth/refresh-token', request_headers={'Authorization': 'Bearer blah di blah 1'}, status_code=200, json={
        "title": "200 OK",
        "detail": "Token refreshed",
        "data": None,
        "meta": {
            "access_token": "blah di blah 2"
        }
    })

    conn.refresh_token()
    conn.refresh_token()

def test_logout(conn: Connection, requests_mock):
    requests_mock.get('https://api.superhero.com.au/auth/logout', status_code=200, json={
        "title": "200 OK",
        "detail": "You have been logged out",
        "data": None,
    })

    conn.logout()

    assert not conn.logged_in

def test_get_holdings(conn: Connection, parser: mock.Mock, requests_mock):
    requests_mock.get('https://api.superhero.com.au/accounts/holding?per_page=9999', request_headers={'Accept': 'application/x.superhero-api.v5+json'}, status_code=200, json={'data': 'sentry', 'meta': {'access_token': 'blah'}})
    conn.get_holdings()
    parser.parse_holdings.assert_called_with("sentry")

def test_get_security_info(conn: Connection, parser: mock.Mock, requests_mock):
    requests_mock.get('https://api.superhero.com.au/securities/123456', status_code=200, json={'data': 'sentry', 'meta': {'access_token': 'blah'}})
    conn.get_security_info(123456)
    parser.parse_security_info.assert_called_with("sentry")

def test_get_security_performance(conn: Connection, parser: mock.Mock, requests_mock):
    requests_mock.get('https://api.superhero.com.au/securities/123456/performance?date_period=5d', status_code=200, json={'data': 'sentry', 'meta': {'access_token': 'blah'}})
    conn.get_security_performance(123456, date_period='5d')
    parser.parse_security_performance.assert_called_with("sentry")

def test_get_security_depth(conn: Connection, parser: mock.Mock, requests_mock):
    requests_mock.get('https://api.superhero.com.au/securities/123456/depth', json={'data': 'sentry', 'meta': {'access_token': 'blah'}})
    conn.get_security_depth(123456)
    parser.parse_security_depth.assert_called_with("sentry")

def test_get_orders(conn: Connection, parser: mock.Mock, requests_mock):
    requests_mock.get('https://api.superhero.com.au/accounts/pending?per_page=9999&status=', json={'data': 'sentry', 'meta': {'access_token': 'blah'}})
    conn.get_orders()
    parser.parse_orders.assert_called_with("sentry")

    requests_mock.get('https://api.superhero.com.au/accounts/pending?per_page=9999&status=PENDING', json={'data': 'sentry2', 'meta': {'access_token': 'blah'}})
    conn.get_orders(OrderStatus.PENDING)
    parser.parse_orders.assert_called_with("sentry2")

def test_cancel_order(conn: Connection, requests_mock):
    requests_mock.delete('https://api.superhero.com.au/orders/123456', json={'data': None, 'meta': {'access_token': 'blah'}})
    conn.cancel_order(123456)

def test_validate_order(conn: Connection, requests_mock):
    requests_mock.post('https://api.superhero.com.au/orders/validate', additional_matcher=lambda request: request.json() == {
        "order_price": 3.55,
        "order_type": "Buy",
        "order_volume": 123,
        "pricing_instruction": "Limit",
        "security_id": 456,
    }, status_code=422, json={
        'errors': {
            'security_id': ['Something is wrong']
        },
        'status_code': 422,
        'meta': {
            'access_token': 'blah'
        }})
    validated, errors = conn.validate_order(456, Price('3.55'), 123, Side.BUY, PricingInstruction.LIMIT)
    assert not validated
    assert errors == {'security_id': ['Something is wrong']}

    requests_mock.post('https://api.superhero.com.au/orders/validate', additional_matcher=lambda request: request.json() == {
        "order_price": 3.55,
        "order_type": "Buy",
        "order_volume": 123,
        "pricing_instruction": "Limit",
        "security_id": 457
    }, request_headers={'Authorization': 'Bearer blah'}, status_code=200, json={'data': 'sentry', 'meta': {'access_token': 'blah'}})
    validated, errors = conn.validate_order(457, Price('3.55'), 123, Side.BUY, PricingInstruction.LIMIT)
    assert validated

def test_create_order(conn: Connection, requests_mock):
    requests_mock.post('https://api.superhero.com.au/orders/validate', json={'data': 'sentry', 'meta': {'access_token': 'blah'}})
    requests_mock.post('https://api.superhero.com.au/orders/create', additional_matcher=lambda request: request.json() == {
        "order_price": 3.55,
        "order_type": "Buy",
        "order_volume": 123,
        "pricing_instruction": "Limit",
        "security_id": 457
    }, json={'data': {'pin_enabled': True, 'order_id': 9876}, 'meta': {'access_token': 'blah'}})
    requests_mock.patch('https://api.superhero.com.au/orders/9876/confirm/pin', additional_matcher=lambda request: request.json() == {
        'pin': 'mypin'
    }, json={'data': {'order_id': 9876}, 'meta': {'access_token': 'blah'}})

    order_id = conn.create_order(457, Price('3.55'), 123, Side.BUY, PricingInstruction.LIMIT)
    assert order_id == 9876

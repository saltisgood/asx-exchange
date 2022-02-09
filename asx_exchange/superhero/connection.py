import logging
import time
import threading

import requests

from paper_trader.utils.price import Price

from ..util.secrets import Secrets
from .parser import MasterParser, parse_holdings, parse_orders, parse_security_depth, parse_security_info, parse_security_performance
from .types import OrderStatus, PricingInstruction, Side

class Connection:
    HOST = 'https://api.superhero.com.au'

    def __init__(self, secrets : Secrets | None =None, parser: MasterParser=MasterParser()):
        """
        bearer = A bearer token, can be obtained by logging in and then taking the last update to the token.
        """

        self._logger = logging.getLogger("asx_exchange.superhero")

        self.__bearer: str | None = None
        self.__last_bearer_update = time.time()
        self.__lock = threading.Lock()
        self.__keep_alive = True

        if secrets is not None:
            superhero_secrets = secrets.get_sub('superhero')
            self._username = superhero_secrets.get_str('username')
            self._password = superhero_secrets.get_str('password')
            self._pin = superhero_secrets.get_str('pin')
        else:
            self._username = None
            self._password = None
            self._pin = None
        
        self._parser = parser
    
    @property
    def logged_in(self):
        return bool(self.__bearer)
    
    def keep_session_alive(self, max_wait=540):
        """
        A looping function that won't return until cancel_keep_alive() is called.
        Will continue refreshing the auth token every max_wait seconds.
        """
        while True:
            while True:
                with self.__lock:
                    if not self.__keep_alive:
                        return
                    
                    if time.time() >= self.__last_bearer_update + max_wait:
                        break
                
                time.sleep(1)
            
            self.refresh_token()
    
    def cancel_keep_alive(self):
        with self.__lock:
            self.__keep_alive = False
    
    def refresh_token(self):
        """
        Refresh the bearer token. Probably needs to be done more frequently than 10 minutes.
        """
        self._make_request('/auth/refresh-token', accept_api=False)
    
    def get_holdings(self):
        """
        Get all your portfolios
        """
        resp = self._make_request('/accounts/holding', params={'per_page': 9999})
        return self._parser.parse_holdings(resp)
    
    def get_security_info(self, security_id: int):
        """
        Get the overall info of a security.
        """
        resp = self._make_request(f'/securities/{security_id}', accept_api=False)
        return self._parser.parse_security_info(resp)
    
    def get_security_performance(self, security_id: int, date_period: str='1d'):
        """
        Get the performance of a security over time.
        The date periods supported on the site are: 1d, 5d, 1m, 6m, 1y, 5y
        """
        resp = self._make_request(f'/securities/{security_id}/performance', accept_api=False, params={'date_period': date_period})
        return self._parser.parse_security_performance(resp)
    
    def get_security_depth(self, security_id: int):
        """
        Get the current market depth (aka orderbook)
        """
        resp = self._make_request(f'/securities/{security_id}/depth', accept_api=False)
        return self._parser.parse_security_depth(resp)
    
    def get_orders(self, status: OrderStatus=OrderStatus.ALL):
        """
        Return the active or cancelled orders
        """
        resp = self._make_request('/accounts/pending', accept_api=False, params={'per_page': 9999, 'status': str(status)})
        return self._parser.parse_orders(resp)
    
    def _get_order_data(self, security_id: int, price: Price, volume: int, side: Side, instruction: PricingInstruction):
        return {
            "order_price": float(price.value),
            "order_type": str(side),
            "order_volume": volume,
            "pricing_instruction": str(instruction),
            "security_id": security_id,
        }
    
    def create_order(self, security_id: int, price: Price, volume: int, side: Side, instruction: PricingInstruction) -> int:
        """
        Submitted after hours uses MarketToLimit if market with a price
        """

        validated, errors = self.validate_order(security_id, price, volume, side, instruction)
        if not validated:
            raise RuntimeError(f"Order validation failed: {errors}")

        data = self._get_order_data(security_id, price, volume, side, instruction)

        if not self._pin:
            raise RuntimeError("PIN not supplied")

        resp = self._make_request(f'/orders/create', accept_api=False, method='post', json=data)
        if resp['pin_enabled']:
            order_id = resp['order_id']
            resp = self._make_request(f'/orders/{order_id}/confirm/pin', accept_api=False, method='patch', json={"pin": self._pin})
        return resp['order_id']
    
    def validate_order(self, security_id: int, price: Price, volume: int, side: Side, instruction: PricingInstruction) -> tuple[bool, dict]:
        """
        Check if an order would be valid
        """

        data = self._get_order_data(security_id, price, volume, side, instruction)

        try:
            self._make_request('/orders/validate', accept_api=False, method='post', json=data)
        except requests.exceptions.HTTPError as e:
            return False, e.response.json()['errors']

        return True, {}
    
    def cancel_order(self, order_id: int):
        self._make_request(f'/orders/{order_id}', accept_api=False, method='delete')
    
    def login(self, username: str | None = None, password: str | None = None):
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'SuperheroApp/2.13.1 Android/11'
        }

        if not username:
            username = self._username
        if not password:
            password = self._password
        if not username or not password:
            raise RuntimeError("Username or password not supplied for login")

        with self.__lock:
            resp = requests.post(f'{self.HOST}/auth/login', headers=headers, json={"email": username, "password": password, "g-recaptcha-response": "1", "isUsingBioAuth": True})
            resp.raise_for_status()
            self._update_token(resp.json())
    
    def logout(self):
        if self.logged_in:
            with self.__lock:
                resp = requests.get(f'{self.HOST}/auth/logout', headers=self._get_headers(accept_api=False))
                resp.raise_for_status()
                self.__bearer = None
    
    def _make_request(self, path: str, accept_api=True, method: str='get', **kwargs):
        with self.__lock:
            self._logger.info("%s %s", method.upper(), path)

            resp = requests.request(method, f'{self.HOST}{path}', headers=self._get_headers(accept_api=accept_api), **kwargs)

            (self._logger.debug if resp.ok else self._logger.error)("%s %s -> [%d %s] took %s", method.upper(), path, resp.status_code, resp.reason, resp.elapsed)
            self._update_token(resp.json())
            resp.raise_for_status()
        return resp.json()['data']
    
    def _get_headers(self, accept_api=True):
        if not self.logged_in:
            raise RuntimeError("Not logged in")
        return {
            'Accept': 'application/x.superhero-api.v5+json' if accept_api else 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Authorization': f'Bearer {self.__bearer}',
            'Origin': 'https://app.superhero.com.au',
            'User-Agent': 'SuperheroApp/2.13.1 Android/11'
        }

    def _update_token(self, resp: dict):
        # Not thread safe, must be called with __lock locked
        self.__bearer = resp['meta']['access_token']
        self.__last_bearer_update = time.time()

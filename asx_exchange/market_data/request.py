import cloudscraper
import logging
import requests
import requests.cookies

from .response import CompaniesListResponse, HistoryResponse, SectorResponse, SymbolResponse

MARKET_HOST = 'https://www.marketindex.com.au'
QUOTE_HOST = 'https://quoteapi.com'

_DEFAULT_HEADERS = {
    QUOTE_HOST: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0', 'Referer': 'https://quoteapi.com'
    },
    MARKET_HOST: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
    }
}
_DEFAULT_PARAMS = {
    QUOTE_HOST: {
        'appID': '02ab19f92cec5cd5',
    },
    MARKET_HOST: {},
}
_COOKIES = requests.cookies.RequestsCookieJar()
_LOGGER = logging.getLogger('asx_exchange.request')

def _host(url: str):
    return '/'.join(url.split('/')[:3])

def _make_request_base(caller, url, params=None, headers=None):
    host = _host(url)
    p = _DEFAULT_PARAMS[host].copy()
    if params:
        p.update(params)

    h = _DEFAULT_HEADERS[host].copy()
    if headers:
        h.update(headers)
    
    _LOGGER.debug("REST call to %s?%s", url, '&'.join(f'{k}={v}' for k, v in p.items()))

    global _COOKIES
    resp = requests.get(url, params=p, headers=h, cookies=_COOKIES)
    _LOGGER.debug("REST call returned with status: %d", resp.status_code)
    resp.raise_for_status()
    _COOKIES = resp.cookies
    return resp

def _make_request_raw(url, params=None, headers=None):
    host = _host(url)
    caller = requests if host == MARKET_HOST else cloudscraper
    return _make_request_base(caller, url, params, headers)

def _make_request(url, params=None, headers=None):
    return _make_request_raw(url, params, headers).json()

def _make_request_text(url, params=None, headers=None):
    return _make_request_raw(url, params, headers).text

class Symbol:
    STUB = '/api/v4/symbols/{symbol}.asx'
    HOST = QUOTE_HOST

    def __init__(self, symbol: str):
        self.symbol = symbol

    def request(self):
        resp = _make_request(self.HOST + self.STUB.format(symbol=self.symbol.lower()), params={'desc': '1', 'liveness': 'delayed'})
        symbol_info = SymbolResponse.parse(resp)
        return SymbolResponse.parse(resp)

class Sector:
    STUB = '/asx/{symbol}'
    HOST = MARKET_HOST

    def __init__(self, symbol: str):
        self.symbol = symbol
    
    def request(self):
        resp = _make_request_text(self.HOST + self.STUB.format(symbol=self.symbol.lower()))
        return SectorResponse.parse(resp)

class History:
    STUB = '/api/v4/symbols/{symbol}.asx/ticks'
    HOST = QUOTE_HOST

    def __init__(self, symbol: str):
        self.symbol = symbol
    
    def request(self, range : str = '2y'):
        resp = _make_request(self.HOST + self.STUB.format(symbol=self.symbol.lower()), params={'fields': 'all', 'range': range})
        return HistoryResponse.parse(resp)

class CompaniesList:
    STUB = '/api/v1/companies'
    HOST = MARKET_HOST

    def request(self):
        resp = _make_request(self.HOST + self.STUB)
        return CompaniesListResponse.parse(resp)
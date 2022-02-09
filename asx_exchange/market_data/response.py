from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import re

from paper_trader.utils import Price
from paper_trader.market_data.types import ClosePrice, ClosePrices, EndOfDay, SymbolInfo

def _get_simple_symbol(sym: str):
    return sym.removesuffix('.asx')

def _get_decimal(val: float):
    if val is not None:
        return Decimal(val).quantize(Decimal('1.0000'))
    return None

def _get_price(val: float):
    if val is not None:
        return Price(val)
    return None

@dataclass(frozen=True)
class SymbolResponse:
    @staticmethod
    def parse(resp: dict):
        symbol = _get_simple_symbol(resp['symbol'])
        currency = resp['currency']
        desc = resp['desc']
        sym_info = SymbolInfo(symbol, desc['name'], desc['issuerName'], desc['longDesc'], currency)
        quote = resp['quote']
        pct_change = _get_decimal(quote['pctChange'])
        eod = EndOfDay(symbol, date.today(), currency, _get_price(quote['low']), _get_price(quote['high']), _get_price(quote['open']), _get_price(quote['close']), _get_price(quote['change']), pct_change, quote['volume'], _get_price(quote['value']))
        return SymbolResponse(sym_info, eod)
    
    symbol_info: SymbolInfo
    end_of_day: EndOfDay

class SectorResponse:
    REGEX = re.compile(r'<tr>\s*<td>Sector</td>\s*<td class="text-right">(.+)</td>')

    @staticmethod
    def parse(html: str):
        match = SectorResponse.REGEX.search(html)
        if match:
            value = match.group(1)
            if value == '-':
                value = ''
            return value

class HistoryResponse:
    @staticmethod
    def parse(resp: dict):
        symbol = _get_simple_symbol(resp['symbol'])
        currency = resp['currency']
        eods = list[EndOfDay]()

        # TODO: handle cases where there was no trading during the period. e.g. ski

        for date_, close, low, open, volume, high, value, prev_close in zip(resp['ticks']['date'], resp['ticks']['close'], resp['ticks']['low'], resp['ticks']['open'], resp['ticks']['volume'], resp['ticks']['high'], resp['ticks']['value'], resp['ticks']['prevClose']):
            # There are some gaps in the data
            if close is None:
                continue
            date_ = date(*(int(x) for x in date_.split('-')))

            if prev_close is None:
                change = Price('0.0')
                pct_change = Decimal('0.0')
            else:
                change = Price(close) - Price(prev_close)
                pct_change = (Decimal(100.0) * change.value / Decimal(prev_close)).quantize(Decimal('0.001'))
            eods.append(EndOfDay(symbol, date_, currency, Price(low), Price(high), Price(open), Price(close), change, pct_change, volume, Price(value)))
        
        return eods

@dataclass(frozen=True)
class CompaniesListResponse:
    @staticmethod
    def parse(resp: list):
        return [CompaniesListResponse(r['code'], r['title']) for r in resp]
    
    symbol: str
    name: str

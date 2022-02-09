from datetime import date, timedelta
from time import sleep

import pandas as pd
from scipy import stats

from paper_trader.db.sqlite import SqliteDb
from paper_trader.interpreter import Interpreter, add_arg
from paper_trader.market_data.types import EndOfDay
from paper_trader.utils.dataclasses import to_pandas
from paper_trader.utils.price import Price

from asx_exchange.superhero.types import OrderStatus, PricingInstruction, Side

from .market_data.index import COMPANIES
from .market_data.request import History
from .superhero import ConnectionProto
from .strategy import LastPriceConditionalOrder, StrategyMaster

def get_tick_size(prices: list[Price]):
    from decimal import Decimal
    import math

    factor = Decimal('100000')
    normed_prices = [int(p.value * factor) for p in prices]

    tick_size = math.gcd(*normed_prices)
    return Price(Decimal(tick_size) / factor)

class AsxInterpreter(Interpreter):
    def __init__(self, conn: ConnectionProto, strategy_master: StrategyMaster, *nargs, **kwargs):
        super().__init__(*nargs, **kwargs)
        self._conn = conn
        self._strategy_master = strategy_master
    
    def __enter__(self):
        return self
    
    def __exit__(self, *nargs, **kwargs):
        if self._conn.logged_in:
            self._conn.logout()

    def cmd_superhero_login(self):
        if not self._conn.logged_in:
            self._conn.login()
        else:
            print('Already logged in', file=self.stdout)
    
    def cmd_superhero_logout(self):
        if self._conn.logged_in:
            self._conn.logout()
        else:
            print("Not logged in", file=self.stdout)
    
    def cmd_get_holdings(self):
        print(self._conn.get_holdings(), file=self.stdout)
    
    @add_arg("security_id", type=int, help="The numerical ID of the security")
    def cmd_get_security_info(self, security_id: int):
        print(self._conn.get_security_info(security_id), file=self.stdout)
    
    @add_arg("security_id", type=int, help="Get the market depth for a security")
    def cmd_get_depth(self, security_id: int):
        depth = self._conn.get_security_depth(security_id)
        print(depth, file=self.stdout)
    
    @add_arg("--status", choices=["pending", "cancelled", "all"], default="all")
    def cmd_get_orders(self, status: str="all"):
        print(self._conn.get_orders(OrderStatus.parse(status)), file=self.stdout)
    
    def cmd_list_strategies(self):
        running, finished = self._strategy_master.get_all()
        if running:
            print("Running strategies:", file=self.stdout)
            for key, strategy in running:
                print(f"{key}: {strategy}", file=self.stdout)
        else:
            print("No running strategies", file=self.stdout)
        
        if finished:
            print("Finished strategies:", file=self.stdout)
            for key, strategy in finished:
                print(f"{key}: {strategy}", file=self.stdout)
        else:
            print("No finished strategies", file=self.stdout)
    
    @add_arg("strategy_key", help="The key of the strategy to stop")
    def cmd_stop_strategy(self, strategy_key: str):
        self._strategy_master.stop_strategy(strategy_key)
    
    def cmd_stop_all_strategies(self):
        self._strategy_master.stop_all()
    
    @add_arg("-s", "--security_id", type=int, required=True, help="The numerical ID of the security")
    @add_arg("-m", "--min_price", required=True, help="The minimum price to watch for")
    @add_arg("-v", "--sell_volume", type=int, required=True, help="The number of items to sell")
    @add_arg("-p", "--sell_price", required=True, help="The price to sell for")
    def cmd_add_conditional_order(self, security_id: int, min_price: str, sell_volume: int, sell_price: str):
        min_price_actual = Price(min_price)
        sell_price_actual = Price(sell_price)

        strat = LastPriceConditionalOrder(self._conn, security_id, min_price_actual, sell_volume, sell_price_actual)
        if strat.validate():
            self._strategy_master.add_strategy(f"{security_id}-conditional-order", strat)

    def cmd_fetch_history(self):
        db = SqliteDb(self._db_file)

        for company in COMPANIES:
            code = company['code']
            
            print(f'Fetching {code}...')
            history_resp = History(code).request(range='2w')
            
            with db:
                db.upsert_all(history_resp)

        sleep(0.5)

        db.close()
    
    @add_arg("-d", "--days", type=int, default=7, help="The number of days to search")
    @add_arg("-n", "--num", type=int, default=20, help="The number of instruments to show")
    def cmd_linear_reg_analysis(self, days: int = 7, num: int=20):
        db = SqliteDb(self._db_file)
        flattened = list(db.get_all(EndOfDay))
        db.close()

        df = to_pandas(flattened)
        df.reset_index(inplace=True)
        df.set_index('date', inplace=True)

        df = df.loc[df.index > (date.today() - timedelta(days=days))]

        trend = pd.DataFrame({'symbol': [], 'start': [], 'slope': [], 'intercept': [], 'r': []}).set_index('symbol')

        symbols = df['symbol'].unique()
        for symbol in symbols:
            symbol_prices = df[df['symbol'] == symbol].copy()
            initial_price = symbol_prices['close'].to_list()[0]
            symbol_prices['normalised_price'] = symbol_prices['close'] * (100. / initial_price)
            res = stats.linregress(list(range(symbol_prices['normalised_price'].size)), symbol_prices['normalised_price'])

            trend.loc[symbol] = [symbol_prices.index[0], res.slope, res.intercept, res.rvalue]
        
        trend = trend.sort_values('slope', ascending=False)
        print(trend.head(num))
    
    def cmd_test(self):
        pass

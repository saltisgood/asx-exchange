import argparse  # pragma: no cover
from datetime import date, datetime, timedelta
from time import sleep
import pdb

from paper_trader.db.sqlite import SqliteDb
from paper_trader.analysis.simulator import Simulation, SimulationRunner, AndFilter, DateFilter, SymbolFilter, filter
from paper_trader.analysis.weekly import DowSimulator, weekly_trend
from paper_trader.exchange.history import PriceTime, SymbolPriceTime
from paper_trader.market_data.types import EndOfDay
from paper_trader.utils.circular_buffer import CircularBufferAdaptor
from paper_trader.utils.dataclasses import to_pandas
from paper_trader.utils.price import Price

from .interpreter import AsxInterpreter
from .main import Main
from .market_data.request import CompaniesList, Symbol, History, Sector
from .market_data.index import ASX200, COMPANIES

import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def fetch():
    db = SqliteDb('test.db3')

    for company in COMPANIES:
        code = company['code']
        if code < 'FATP':
            continue
        #if code in ASX200.keys():
            #continue
        
        print(f'Fetching {code}...')
        #symbol_resp = Symbol(code).request()
        history_resp = History(code).request(range='2w')
        
        with db:
            db.upsert_all(history_resp)

        sleep(0.5)

    db.close()
    return

    for code in ASX200.keys():
        ##breakpoint()
        print(f'Fetching {code}...')
        symbol_resp = Symbol(code).request()
        history_resp = History(code).request()
        
        with db:
            db.upsert(symbol_resp.symbol_info)
            db.upsert(symbol_resp.end_of_day)
            db.upsert_all([SymbolPriceTime(history_resp.symbol, c.price, datetime(c.date.year, c.date.month, c.date.day)) for c in history_resp.closes])

        sleep(1)

    db.close()

def fetchflt():
    db = SqliteDb('test.db3')

    history_resp = History('flt').request()
    with db:
        db.upsert_all(history_resp)
    db.close()
    return

def fetch_companies():
    companies = CompaniesList().request()
    for company in companies:
        sector = Sector(company.symbol).request()
        if sector:
            print(f'{company}: {sector}')
        else:
            print(f'{company} not found')
        sleep(0.05)

def pandas():
    db = SqliteDb('test.db3')
    #flattened = list(db.get_all(SymbolPriceTime))
    try:
        flattened = list(db.get_all(EndOfDay))
    except:
        pdb.post_mortem()
    db.close()

    df = to_pandas(flattened)
    df.reset_index(inplace=True)
    #df.set_index('time', inplace=True)
    df.set_index('date', inplace=True)

    df = df.loc[df.index > (date.today() - timedelta(days=7))]
    #df = df.loc[df.index > (datetime.utcnow() - timedelta(days=7))]

    trend = pd.DataFrame({'symbol': [], 'start': [], 'slope': [], 'intercept': [], 'r': []}).set_index('symbol')

    #breakpoint()
    symbols = df['symbol'].unique()
    for symbol in symbols:
        symbol_prices = df[df['symbol'] == symbol].copy()
        initial_price = symbol_prices['close'].to_list()[0]
        symbol_prices['normalised_price'] = symbol_prices['close'] * (100. / initial_price)
        res = stats.linregress(list(range(symbol_prices['normalised_price'].size)), symbol_prices['normalised_price'])

        trend.loc[symbol] = [symbol_prices.index[0], res.slope, res.intercept, res.rvalue]

        #axis = plt.subplot()
        #symbol_prices.plot(ax=axis)
        #axis.set_title(symbol)
        #plt.show(block=True)
    
    trend = trend.sort_values('slope', ascending=False)
    print(trend.head(20))
    #print(trend.tail(10))
    #print(trend['slope'].max())

def dow_analysis():
    db = SqliteDb('test.db3')
    flattened = list(db.get_all(SymbolPriceTime))
    db.close()
    
    best_ave_pct = None
    best_ave = None
    best_med_pct = None
    best_med = None
    best_days_count = None
    best_days = None
    best_adj_pct = None
    best_adj = None
    #symbols = {spt.symbol for spt in flattened}
    symbols = {'chn'}
    for symbol in symbols:
        if symbol == 'gxy':
            continue
        #print(f'\nFor {symbol}:')
        #trend = weekly_trend([PriceTime(spt.price, spt.time) for spt in flattened if spt.symbol == symbol])
        trend = weekly_trend([PriceTime(spt.price, spt.time) for spt in (flattened | filter(AndFilter([SymbolFilter(symbol), DateFilter(back_time=timedelta(days=30))])))])
        #print(trend)

        fri = trend.days[4]
        if fri:
            if best_ave_pct is None or fri.ave_diff_pct > best_ave_pct:
                best_ave_pct = fri.ave_diff_pct
                best_ave = (symbol, trend)
            if best_med_pct is None or fri.median_diff_pct > best_med_pct:
                best_med_pct = fri.median_diff_pct
                best_med = (symbol, trend)
        continue


        days = [d for d in trend.days if d]
        if days:
            max_ave_pct = max(d.ave_diff_pct for d in days)
            max_med_pct = max(d.median_diff_pct for d in days)
            max_days = max(d.positive_days for d in days)
            if best_ave_pct is None or max_ave_pct > best_ave_pct:
                best_ave_pct = max_ave_pct
                best_ave = (symbol, trend)
            if best_med_pct is None or max_med_pct > best_med_pct:
                best_med_pct = max_med_pct
                best_med = (symbol, trend)
            if best_days_count is None or max_days > best_days_count:
                best_days_count = max_days
                best_days = (symbol, trend)
            circular_days = CircularBufferAdaptor(days)
            for d in range(5):
                c_days = list(circular_days.from_offset(d))
                diff = c_days[1].ave_diff_pct - c_days[0].ave_diff_pct
                if best_adj_pct is None or diff > best_adj_pct:
                    best_adj_pct = diff
                    best_adj = (symbol, trend)

    
    print(f'\nBest average trend is for {best_ave[0]}\n{best_ave[1]}')
    print(f'\nBest median trend is for {best_med[0]}\n{best_med[1]}')
    #print(f'\nBest days trend is for {best_days[0]}\n{best_days[1]}')
    #print(f'\nBest adjacent trend is for {best_adj[0]}\n{best_adj[1]}')

def dow_simulation():
    db = SqliteDb('test.db3')
    flattened = list(db.get_all(SymbolPriceTime))
    db.close()

    runner = SimulationRunner(flattened)
    simulator = DowSimulator(Simulation(), Price('10000.0'))
    runner.run(simulator, AndFilter([SymbolFilter({'chn'}), DateFilter(back_time=timedelta(days=50))]))

def interpreter():
    from .strategy import StrategyMaster
    from .superhero import Connection
    from .util.secrets import Secrets
    import threading

    secrets = Secrets.from_file()
    conn = Connection(secrets)

    #t = threading.Thread(target=conn.keep_session_alive, args=(540,))
    #t.start()

    strats = StrategyMaster()

    with AsxInterpreter(conn, strats, db_file='test.db3') as interp:
        interp.cmdloop()

    #conn.cancel_keep_alive()
    #t.join()

    strats.stop_all()

def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="asx_exchange.",
        epilog="Enjoy the asx_exchange functionality!",
    )
    parser.add_argument(
        '-f',
        '--file',
        default='test.db3',
        help='The DB filename to use'
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Optionally adds verbosity",
    )
    args = parser.parse_args()

    interpreter()
    exit()

    #fetchflt()
    #exit()
    #fetch_companies()
    #exit()

    #fetch()
    pandas()
    #dow_analysis()
    #dow_simulation()
    exit()

    #m = Main(args.file, args.verbose)
    #cmdloop(m)
    #return

    
    #breakpoint()
    #runner = SimulationRunner(flattened[3 * (len(flattened) // 4):])
    #simulator = DowSimulator(Simulation(), Price('50000.0'))
    #runner.run(simulator)

    #db = SqliteDb('test.db3')

    #for code in ASX200.keys():
        #if code < 'SLK':
            #continue
        #if code == 'ORE' or code == 'SLK':
            #continue
        ##breakpoint()
        #print(f'Fetching {code}...')
        #symbol_resp = Symbol(code).request()
        #history_resp = History(code).request()
        
        #with db:
            #db.upsert(symbol_resp.symbol_info)
            #db.upsert(symbol_resp.end_of_day)
            #db.upsert_all([SymbolPriceTime(history_resp.symbol, c.price, datetime(c.date.year, c.date.month, c.date.day)) for c in history_resp.closes])

        #sleep(1)

    #db.close()
    exit()

    symbol_resp = Symbol('FLT').request()
    print(str(symbol_resp))

    #history_resp = History('FLT').request()
    #print(str(history_resp))

    with SqliteDb('test.db3') as db:
        #db.init_table(type(symbol_resp.symbol_info))
        #db.upsert(symbol_resp.symbol_info)

        db.init_table(type(symbol_resp.end_of_day))
        db.upsert(symbol_resp.end_of_day)

if __name__ == "__main__":  # pragma: no cover
    main()

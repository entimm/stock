import datetime

import pandas as pd
from mootdx.reader import Reader

from common.common import GNBK_FILE_PATH, STOCK_META_FILE_PATH, ETF_FILE_PATH, TDX_PATH

stock_meta_df = pd.read_csv(STOCK_META_FILE_PATH, dtype={1: str, 6: str})
symbol_name_dict = dict(zip(stock_meta_df['symbol'], stock_meta_df['name']))

gnbk_df = pd.read_csv(GNBK_FILE_PATH, dtype={0: str})
gnbk_dict = dict(zip(gnbk_df['symbol'], gnbk_df['name']))

etf_df = pd.read_csv(ETF_FILE_PATH, dtype={0: str})
etf_dict = dict(zip(etf_df['symbol'], etf_df['name']))

local_tdx_reader = Reader.factory(market='std', tdxdir=TDX_PATH)
trade_date_list = local_tdx_reader.daily(symbol='999999').reset_index().tail(200)['date'].to_list()

YEAR = datetime.datetime.now().year

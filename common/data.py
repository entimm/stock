import pandas as pd

from common.common import GNBK_FILE_PATH, STOCK_META_FILE_PATH

stock_meta_df = pd.read_csv(STOCK_META_FILE_PATH, dtype={1: str})
symbol_name_dict = dict(zip(stock_meta_df['symbol'], stock_meta_df['name']))

gnbk_df = pd.read_csv(GNBK_FILE_PATH, dtype={0: str})
gnbk_dict = dict(zip(gnbk_df['symbol'], gnbk_df['name']))
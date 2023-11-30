import json
import os

import pandas as pd

from common.common import GNBK_FILE_PATH, STOCK_META_FILE_PATH, ETF_FILE_PATH, INDEX_FILE_PATH, RESOURCES_PATH

stock_meta_df = pd.read_csv(STOCK_META_FILE_PATH, dtype={1: str, 6: str})
ticker_name_dict = dict(zip(stock_meta_df['symbol'], stock_meta_df['name']))

gnbk_df = pd.read_csv(GNBK_FILE_PATH, dtype={0: str})
gnbk_dict = dict(zip(gnbk_df['symbol'], gnbk_df['name']))

etf_df = pd.read_csv(ETF_FILE_PATH, dtype={0: str})
etf_dict = dict(zip(etf_df['symbol'], etf_df['name']))

index_df = pd.read_csv(INDEX_FILE_PATH, dtype={0: str})
index_dict = dict(zip(index_df['symbol'], index_df['name']))

with open(os.path.join(RESOURCES_PATH, 'xuangubao', 'limited_up_total_dict.json'), 'r') as file:
    limited_up_total_dict = json.load(file)
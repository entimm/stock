import json
import os
from datetime import datetime
from functools import cmp_to_key

import click
import pandas as pd

from common import price_calculate
from common.cmd_utils import custom_compare_desc, custom_compare_asc
from common.const import RESOURCES_PATH, YEAR
from common.quotes import trade_date_list, fetch_local_daily
from common.utils import ticker_name


@click.command()
@click.argument('ma_v', default=3, type=int)
@click.argument('year', default=YEAR, type=int)
def cal_trend_ptg(ma_v, year):
    data_len = 2000
    direction = 1

    date_list = trade_date_list['date'].tail(data_len).to_list()
    result_json_file = os.path.join(RESOURCES_PATH, 'trends', f'MA{ma_v}_trend_{year}.json')
    result_dict = {}
    if os.path.exists(result_json_file):
        with open(result_json_file, 'r') as file:
            result_dict = json.load(file)
            latest_date = list(result_dict.keys())[-2]

        if latest_date:
            date_list = [item for item in date_list if item > datetime.strptime(latest_date, "%Y-%m-%d")]
            data_len = len(date_list)

    df = pd.read_csv(os.path.join(RESOURCES_PATH, 'a_stock_meta_list.csv'), dtype={0: str, 1: str})
    df = df.sort_values(by='list_date', ascending=False)
    df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
    symbols = df['symbol'].to_list()

    i = 0
    stock_data = {}
    for symbol in symbols:
        # print(f'trend-cal {year}-{ma_v} {i}: {symbol}')
        i += 1
        one_df = fetch_local_daily(symbol=symbol).reset_index().tail(data_len + 500)
        one_df = one_df.reset_index()

        one_df[f'MA{ma_v}'] = price_calculate.ma(one_df, ma_v)
        one_df[f'MA{ma_v}_angle'] = price_calculate.ma_angle(one_df, f'MA{ma_v}')
        condition = one_df[f'MA{ma_v}_angle'] >= 0 if direction == 1 else one_df[f'MA{ma_v}_angle'] <= 0
        one_df[f'MA{ma_v}_trend'] = price_calculate.ma_trend(one_df, condition)

        one_df['ptc_charge'] = ((one_df['close'] / one_df['close'].shift(1)) - 1) * 100

        stock_data[symbol] = one_df

    for date in date_list:
        if date.year != year:
            continue
        date_str = date.strftime('%Y-%m-%d')
        temp_list = []
        for symbol, stock_df in stock_data.items():
            idx = stock_df[stock_df['date'] == date].index
            if not idx.empty:
                ptc_charge = stock_df.loc[idx, 'ptc_charge'].values[0]
                value = stock_df.loc[idx, f'MA{ma_v}_trend'].values[0]
                temp_list.append((f'{ticker_name(symbol)}|{symbol}|{round(ptc_charge, 2)}|{round(value, 2)}', value))

        # 长度不齐就补空白
        temp_list = temp_list + [('-', None)] * (len(symbols) - len(temp_list))

        custom_compare_method = custom_compare_desc if direction == 1 else custom_compare_asc
        sorted_list = [item[0] for item in sorted(temp_list, key=cmp_to_key(custom_compare_method))]
        sorted_list = sorted_list[0: 50]

        print(f'sort {year}-{ma_v}: ' + date_str)
        result_dict[date_str] = sorted_list

    with open(result_json_file, 'w') as json_file:
        json.dump(result_dict, json_file)




import json
import os
import time
from functools import cmp_to_key

import click
import pandas as pd
import requests
from pandas import Timestamp

from common import price_calculate
from common.cmd_utils import custom_compare_desc, custom_compare_asc
from common.const import PUBLIC_PATH, RESOURCES_PATH
from common.quotes import trade_date_list, fetch_local_daily
from common.utils import get_exchange_code, ticker_name
from controllers.limited_power_controller import XUANGUBAO_DETAIL_PATH

@click.command()
def download_fs_img():
    for ts in trade_date_list.tail(1)['date'].to_list()[::-1]:
        date_str2 = ts.strftime('%Y-%m-%d')

        min_img_path = os.path.join(PUBLIC_PATH, 'static/imgs/min', date_str2)
        if not os.path.exists(min_img_path):
            os.mkdir(min_img_path)

        daily_img_path = os.path.join(PUBLIC_PATH, 'static/imgs/daily', date_str2)
        if not os.path.exists(daily_img_path):
            os.mkdir(daily_img_path)

        for symbol in get_symbol_list():
            code = get_exchange_code(symbol)
            timestamp = int(time.time())

            target_file = os.path.join(min_img_path, f'{symbol}.gif')
            if not os.path.exists(target_file):
                img_url = 'https://image2.sinajs.cn/newchart/min/n/{}.gif?t={}'.format(code, timestamp)
                download_image(img_url, target_file)

            target_file = os.path.join(daily_img_path, f'{symbol}.gif')
            if not os.path.exists(target_file):
                img_url = 'https://image2.sinajs.cn/newchart/daily/n/{}.gif?t={}'.format(code, timestamp)
                download_image(img_url, target_file)


def get_symbol_list():
    symbol_list = set()
    for sub_ts in trade_date_list.tail(5)['date'].to_list():
        date = sub_ts.strftime('%Y%m%d')
        file_path = os.path.join(XUANGUBAO_DETAIL_PATH, f'detail-{date}.csv')
        if not os.path.exists(file_path):
            print(f'{date}数据不存在')
            continue
        df = pd.read_csv(file_path)
        symbol_list = symbol_list.union(set(df['symbol'].str[:6].to_list()))

    return symbol_list


@click.argument('ma_v', default=3, type=int)
@click.command()
def cal_limit_up_trend(ma_v):
    direction = 1

    date_list = trade_date_list['date'].tail(1).to_list()
    date_list = [item for item in date_list if item >= Timestamp('2024-01-26')]
    result_json_file = os.path.join(RESOURCES_PATH, 'trends2', f'MA{ma_v}_trend.json')

    result_dict = {}
    if os.path.exists(result_json_file):
        with open(result_json_file, 'r') as file:
            result_dict = json.load(file)

    symbols = get_symbol_list()

    i = 0
    stock_data = {}
    for symbol in symbols:
        print(f'trend-cal: {i}')
        i += 1
        one_df = fetch_local_daily(symbol=symbol).reset_index().tail(len(date_list) + 200)
        one_df = one_df.reset_index()

        one_df[f'MA{ma_v}'] = price_calculate.ma(one_df, ma_v)
        one_df[f'MA{ma_v}_angle'] = price_calculate.ma_angle(one_df, f'MA{ma_v}')
        condition = one_df[f'MA{ma_v}_angle'] >= 0 if direction == 1 else one_df[f'MA{ma_v}_angle'] <= 0
        one_df[f'MA{ma_v}_trend'] = price_calculate.ma_trend(one_df, condition)

        one_df['ptc_charge'] = ((one_df['close'] / one_df['close'].shift(1)) - 1) * 100

        stock_data[symbol] = one_df

    for date in date_list:
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

        print('sort: ' + date_str)
        result_dict[date_str] = sorted_list

    with open(result_json_file, 'w') as json_file:
        json.dump(result_dict, json_file)


def download_image(url, save_path):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"下载图片失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"下载图片时发生错误: {e}")

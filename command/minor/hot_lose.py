import json
import os

import click
import pandas as pd

from common.common import TOTAL_PATH, RESOURCES_PATH
from common.quotes import trade_date_list


@click.command()
def hot_lose():
    result = {}

    yesterday_limit_up_list = []
    for ts in trade_date_list['date'].to_list():
        date = ts.strftime('%Y%m%d')
        date2 = ts.strftime('%Y-%m-%d')
        csv_file = os.path.join(TOTAL_PATH, f'data_{date}.csv')
        if not os.path.exists(csv_file): continue
        df = pd.read_csv(csv_file)
        df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
        df['ts_code'] = df['ts_code'].str[:6]

        if yesterday_limit_up_list:
            df_limit_down = df[df['low'] == df['close']]
            df_limit_down = df_limit_down[df_limit_down['pct_chg'] <= -9.8]
            limit_down_list = df_limit_down['ts_code'].to_list()
            limit_down_list = set(limit_down_list) & set(yesterday_limit_up_list)

            df_big_noodle = df[(df['close'] / df['high'] - 1) * 100 <= -9.8]
            big_noodle_list = df_big_noodle['ts_code'].to_list()
            big_noodle_list = set(big_noodle_list) & set(yesterday_limit_up_list)

            result[date2] = []
            result[date2].append(list(limit_down_list))
            result[date2].append(list(big_noodle_list))

        df = df[df['high'] == df['close']]
        df = df[df['pct_chg'] >= 9.8]
        yesterday_limit_up_list = df['ts_code'].to_list()

    result_json_file = os.path.join(RESOURCES_PATH, f'hot_lose.json')
    with open(result_json_file, 'w') as json_file:
        json.dump(result, json_file)

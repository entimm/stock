import json
import os

import click
import pandas as pd

from common.const import TOTAL_PATH, RESOURCES_PATH
from common.quotes import trade_date_list


@click.command()
def main_army_up():
    result_dict = {}
    result_json_file = os.path.join(RESOURCES_PATH, f'main_army_up.json')
    latest_date = '1990-01-01'
    if os.path.exists(result_json_file):
        with open(result_json_file, 'r') as file:
            result_dict = json.load(file)
            latest_date = list(result_dict.keys())[-1]

    for ts in trade_date_list['date'].to_list():
        date = ts.strftime('%Y%m%d')
        date2 = ts.strftime('%Y-%m-%d')
        if date2 <= latest_date:
            continue
        csv_file = os.path.join(TOTAL_PATH, f'data_{date}.csv')
        if not os.path.exists(csv_file): continue
        df = pd.read_csv(csv_file)

        df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
        df['ts_code'] = df['ts_code'].str[:6]
        df = df[df['pct_chg'] >= 3]
        df = df[df['amount'] >= 2 * 10 ** 6]
        df = df[['ts_code', 'pct_chg', 'amount']]
        df['amount'] = round(df['amount'] / 100000, 2)
        df = df.sort_values(by='amount', ascending=False)
        result_dict[date2] = df.to_dict(orient='records')

    with open(result_json_file, 'w') as json_file:
        json.dump(result_dict, json_file)


@click.command()
def main_army_down():
    result_dict = {}
    result_json_file = os.path.join(RESOURCES_PATH, f'main_army_down.json')
    latest_date = '1990-01-01'
    if os.path.exists(result_json_file):
        with open(result_json_file, 'r') as file:
            result_dict = json.load(file)
            latest_date = list(result_dict.keys())[-1]

    for ts in trade_date_list['date'].to_list():
        date = ts.strftime('%Y%m%d')
        date2 = ts.strftime('%Y-%m-%d')
        if date2 <= latest_date:
            continue
        csv_file = os.path.join(TOTAL_PATH, f'data_{date}.csv')
        if not os.path.exists(csv_file): continue
        df = pd.read_csv(csv_file)

        df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
        df['ts_code'] = df['ts_code'].str[:6]
        df = df[df['pct_chg'] <= -3]
        df = df[df['amount'] >= 2 * 10 ** 6]
        df = df[['ts_code', 'pct_chg', 'amount']]
        df['amount'] = round(df['amount'] / 100000, 2)
        df = df.sort_values(by='amount', ascending=False)
        result_dict[date2] = df.to_dict(orient='records')

    result_json_file = os.path.join(RESOURCES_PATH, f'main_army_down.json')
    with open(result_json_file, 'w') as json_file:
        json.dump(result_dict, json_file)

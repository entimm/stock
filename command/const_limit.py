import json
import os
from datetime import datetime

import click
import pandas as pd

from common.const import YEAR, RESOURCES_PATH
from common.quotes import trade_date_list

XUANGUBAO_DETAIL_PATH = os.path.join(RESOURCES_PATH, 'xuangubao/details')


@click.command()
@click.argument('year', default=YEAR, type=int)
def const_limit(year):
    date_list = trade_date_list['date'].tail(2000).to_list()
    result_json_file = os.path.join(RESOURCES_PATH, 'trends2', f'const_limit.json')
    result_dict = {}
    if os.path.exists(result_json_file):
        with open(result_json_file, 'r') as file:
            result_dict = json.load(file)
            latest_date = list(result_dict.keys())[-1]

        if latest_date:
            date_list = [item for item in date_list if item > datetime.strptime(latest_date, "%Y-%m-%d")]

    for ts in date_list:
        date2 = ts.strftime('%Y-%m-%d')

        if ts.year != year:
            continue

        file_path = os.path.join(XUANGUBAO_DETAIL_PATH, f'detail-{ts.strftime("%Y%m%d")}.csv')
        df = pd.read_csv(file_path, index_col="symbol")
        df = df[['stock_chi_name', 'limit_up_days', 'm_days_n_boards_days', 'm_days_n_boards_boards']]
        df.index = df.index.astype(str).str[:6]

        df = df[df['limit_up_days'] >= 2]
        df = df.sort_values(by='limit_up_days', ascending=False)

        df['show'] = df['stock_chi_name'].astype(str) + '|' + df.index.astype(str) + '|0|' + df['limit_up_days'].astype(str)
        result_dict[date2] = df['show'].to_list()

    with open(result_json_file, 'w') as json_file:
        json.dump(result_dict, json_file)

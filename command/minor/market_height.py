import json
import os
from datetime import datetime

import click
import pandas as pd

from common.const import RESOURCES_PATH
from common.quotes import trade_date_list

XUANGUBAO_DETAIL_PATH = os.path.join(RESOURCES_PATH, 'xuangubao/details')


@click.command()
def market_height():
    result = {}
    date_list = trade_date_list['date'].tail(500).to_list()
    for ts in date_list:
        date = ts.strftime('%Y%m%d')
        date2 = ts.strftime('%Y-%m-%d')
        file_path = os.path.join(XUANGUBAO_DETAIL_PATH, f'detail-{date}.csv')
        df = pd.read_csv(file_path)
        df = df[['stock_chi_name', 'limit_up_days', 'm_days_n_boards_days', 'm_days_n_boards_boards', 'first_limit_up', 'last_limit_up', 'symbol']]
        df = df[~df['stock_chi_name'].str.contains("ST")]
        df['name'] = df.apply(transform_function, axis=1)
        df = df.groupby('limit_up_days').apply(lambda group: group['name'].to_list())
        result[date2] = dict(sorted(df.to_dict().items()))

    with open(os.path.join(RESOURCES_PATH, 'market_height.json'), 'w') as json_file:
        json.dump(result, json_file)


def transform_function(row):
    name = row['stock_chi_name']
    time_str = datetime.fromtimestamp(row['first_limit_up']).strftime('%H:%M')

    if time_str == '09:25' and row['first_limit_up'] == row['last_limit_up']:
        name = f'_{name}_'

    if row['symbol'][0: 2] in ['68', '30']:
        name = f'@{name}'

    return name

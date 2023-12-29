import json
import os

import click
import pandas as pd

from common.common import RESOURCES_PATH
from common.quotes import trade_date_list
from common.utils import send_request
from common.xuangubao import row2info

xuangubao_url = 'https://flash-api.xuangubao.cn/api'


@click.command()
def download_xuangubao_plates():
    for ts in trade_date_list.tail(1000)['date'].to_list()[::-1]:
        date_str = ts.strftime('%Y%m%d')
        file_path = os.path.join(RESOURCES_PATH, 'xuangubao', 'plates', f'plates-{date_str}.csv')
        if os.path.exists(file_path):
            continue

        print(f"date={date_str}")
        url = f'{xuangubao_url}/surge_stock/plates?date={int(ts.timestamp())}'
        data_dict = send_request(url)

        if 'items' not in data_dict['data']:
            print('空数据')
            continue

        items = data_dict['data']['items']
        df = pd.DataFrame(items, columns=['id', 'name', 'description'])

        df.to_csv(file_path, index=False)


@click.command()
def download_xuangubao_stock():
    for ts in trade_date_list.tail(1000)['date'].to_list()[::-1]:
        date_str = ts.strftime('%Y%m%d')
        file_path = os.path.join(RESOURCES_PATH, 'xuangubao', 'stocks', f'stock-{date_str}.csv')
        if os.path.exists(file_path):
            continue

        print(f"date={date_str}")
        url = f'{xuangubao_url}/surge_stock/stocks?date={date_str}&normal=true&uplimit=true'
        data_dict = send_request(url)

        fields = data_dict['data']['fields']
        items = data_dict['data']['items']

        df = pd.DataFrame(items, columns=fields)

        df.to_csv(file_path, index=False)


@click.command()
def download_xuangubao_detail():
    for ts in trade_date_list.tail(1000)['date'].to_list()[::-1]:
        date_str = ts.strftime('%Y%m%d')
        date_str2 = ts.strftime('%Y-%m-%d')
        file_path = os.path.join(RESOURCES_PATH, 'xuangubao', 'details', f'detail-{date_str}.csv')
        if os.path.exists(file_path):
            continue

        print(f"date={date_str}")
        url = f'{xuangubao_url}/pool/detail?pool_name=limit_up&date={date_str2}'
        data_dict = send_request(url)
        if data_dict['data'] is None:
            continue

        df = pd.json_normalize(data_dict['data'])

        df.to_csv(file_path, index=False)


@click.command()
def arrange_xuangubao_detail():
    stock_total_dict = {}
    for ts in trade_date_list.tail(2000)['date'].to_list()[::-1]:
        date_str = ts.strftime('%Y%m%d')
        file_path = os.path.join(RESOURCES_PATH, 'xuangubao', 'details', f'detail-{date_str}.csv')
        if not os.path.exists(file_path):
            continue

        count_dict = {}
        df = pd.read_csv(file_path)
        for index, row in df.iterrows():
            related_plates = []
            if ('surge_reason.related_plates' in row) and (not isinstance(row['surge_reason.related_plates'], float)):
                related_plates = json.loads(row['surge_reason.related_plates'].translate(str.maketrans({'"': "'", "'": '"', '\\': '\\\\'})))
                related_plates = [d for d in related_plates if d]
                for item in related_plates:
                    count_dict.setdefault(item['plate_name'], 0)
                    count_dict[item['plate_name']] += 1
            df.at[index, 'surge_reason.related_plates'] = json.dumps(related_plates)

        for _, row in df.iterrows():
            related_plates = json.loads(row['surge_reason.related_plates'])
            for index, item in enumerate(related_plates):
                related_plates[index]['count'] = count_dict[item['plate_name']]
            symbol = row['symbol'][0:-3]
            if symbol in stock_total_dict:
                continue

            info = row2info(row.to_dict())
            info['date'] = date_str
            info['plates'] = related_plates

            stock_total_dict[symbol] = info

    with open(os.path.join(RESOURCES_PATH, 'xuangubao', 'limited_up_total_dict.json'), 'w') as json_file:
        json.dump(stock_total_dict, json_file)

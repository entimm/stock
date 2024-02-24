import json
import os

import click
import pandas as pd

from common.const import RESOURCES_PATH
from common.quotes import trade_date_list
from common.utils import send_request
from common.xuangubao import row2info

xuangubao_url = 'https://flash-api.xuangubao.cn/api'

# 热点解读
# https://flash-api.xuangubao.cn/api/surge_stock/stocks?date=20190508&normal=true&uplimit=true

@click.command()
def download_xuangubao_detail():
    for ts in trade_date_list.tail(100)['date'].to_list()[::-1]:
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

        for item in data_dict['data']:
            surge_reason = item.get('surge_reason', {})
            surge_reason = surge_reason if surge_reason else {}
            item['reason_desc'] = surge_reason.get('stock_reason', '')
            item['related_plates'] = '##'.join([sub.get('plate_name', '空') + '||' + sub.get('plate_reason', '空') for sub in surge_reason.get('related_plates', [])])

        df = pd.DataFrame(data_dict['data'], columns=[
            "break_limit_up_times",
            "buy_lock_volume_ratio",
            "change_percent",
            "first_limit_up",
            "last_limit_up",
            "is_new_stock",
            "issue_price",
            "limit_up_days",
            "listed_date",
            "m_days_n_boards_boards",
            "m_days_n_boards_days",
            "non_restricted_capital",
            "sell_lock_volume_ratio",
            "stock_chi_name",
            "stock_type",
            "reason_desc",
            "related_plates",
            "symbol",
            "total_capital",
            "turnover_ratio",
            "volume_bias_ratio",
        ])

        df.to_csv(file_path, index=False)


@click.command()
def arrange_xuangubao_detail():
    stock_total_dict = {}
    for ts in trade_date_list.tail(2000)['date'].to_list()[::-1]:
        date_str = ts.strftime('%Y%m%d')
        file_path = os.path.join(RESOURCES_PATH, 'xuangubao/details', f'detail-{date_str}.csv')
        if not os.path.exists(file_path):
            continue

        count_dict = {}
        df = pd.read_csv(file_path, dtype={'related_plates': str})
        df['related_plates'].fillna(value='', inplace=True)
        for index, row in df.iterrows():
            if not row['related_plates']: continue
            related_plates = row['related_plates'].split('##')
            related_plates = [parts[0] for parts in (item.split('||') for item in related_plates)]
            for item in related_plates:
                count_dict.setdefault(item, 0)
                count_dict[item] += 1

        for _, row in df.iterrows():
            related_plates = []
            if row['related_plates']:
                related_plates = row['related_plates'].split('##')
                related_plates = [{'plate_name': parts[0], 'plate_reason': parts[1]} for parts in (item.split('||') for item in related_plates)]
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

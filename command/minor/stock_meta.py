import os

import click
import tushare as ts

from common.common import RESOURCES_PATH, TUSHARE_TOKEN


@click.command()
def stock_meta():
    pro = ts.pro_api(TUSHARE_TOKEN)

    # 拉取数据
    df = pro.stock_basic(**{
        'ts_code': '',
        'name': '',
        'exchange': '',
        'market': '',
        'is_hs': '',
        'list_status': '',
        'limit': '',
        'offset': ''
    }, fields=[
        'ts_code',
        'symbol',
        'name',
        'area',
        'industry',
        'market',
        'list_date'
    ])

    df.to_csv(os.path.join(RESOURCES_PATH, 'a_stock_meta_list.csv'), index=False)

import os
import time

import click
import pandas as pd
import requests

from common.const import PUBLIC_PATH
from common.quotes import trade_date_list
from common.utils import get_exchange_code
from controllers.limited_power_controller import XUANGUBAO_DETAIL_PATH


@click.command()
def download_fs_img():
    for ts in trade_date_list.tail(1)['date'].to_list()[::-1]:
        date_str2 = ts.strftime('%Y-%m-%d')
        img_path = os.path.join(PUBLIC_PATH, 'static/imgs', date_str2)
        if not os.path.exists(img_path):
            os.mkdir(img_path)

        symbol_list = set()
        for sub_ts in trade_date_list.tail(3)['date'].to_list():
            date = sub_ts.strftime('%Y%m%d')
            file_path = os.path.join(XUANGUBAO_DETAIL_PATH, f'detail-{date}.csv')
            if not os.path.exists(file_path): continue
            df = pd.read_csv(file_path)
            symbol_list = symbol_list.union(set(df['symbol'].str[:6].to_list()))

        for symbol in symbol_list:
            code = get_exchange_code(symbol)
            timestamp = int(time.time())
            target_file = os.path.join(img_path, f'{symbol}.gif')
            if not os.path.exists(target_file):
                img_url = f'https://image2.sinajs.cn/newchart/min/n/{code}.gif?t=${timestamp}'
                download_image(img_url, target_file)


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

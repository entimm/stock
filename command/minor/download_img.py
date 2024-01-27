import os
import time

import click
import requests

from common.const import RAW_V2_PATH, RESOURCES_PATH, PUBLIC_PATH
from common.quotes import trade_date_list
from common.tdx import read_tdx_text
from common.utils import get_exchange_code


@click.command()
def download_fs_img():
    directory_path = os.path.join(RAW_V2_PATH, '全部Ａ股')
    for ts in trade_date_list.tail(1)['date'].to_list()[::-1]:
        date = ts.strftime('%Y%m%d')
        date_str2 = ts.strftime('%Y-%m-%d')
        img_path = os.path.join(PUBLIC_PATH, 'imgs', date_str2)
        if not os.path.exists(img_path):
            os.mkdir(img_path)
        file_path = os.path.join(directory_path, f'全部Ａ股{date}.txt')
        df = read_tdx_text(file_path)
        df = df[df['上次涨停'] <= 2]
        for index, row in df.iterrows():
            symbol = row['代码']
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

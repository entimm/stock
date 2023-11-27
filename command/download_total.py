import os

import click
import tushare as ts

from common.common import TOTAL_PATH, TUSHARE_TOKEN
from common.quotes import trade_date_list


@click.command()
def download_total():
    pro = ts.pro_api(TUSHARE_TOKEN)

    for current_date in trade_date_list[::-1]:
        current_date = current_date.strftime('%Y%m%d')
        df = pro.daily(trade_date=current_date)

        file_path = os.path.join(TOTAL_PATH, f'data_{current_date}.csv')

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                line_count = sum(1 for _ in file)
                if line_count > 1000:
                    break

        df.to_csv(file_path, index=False)

        print(f'Data for {current_date} saved to {file_path}')

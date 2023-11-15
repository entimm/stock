import datetime
import os

import click
import tushare as ts

from common.common import TOTAL_PATH, TUSHARE_TOKEN


@click.command()
def download_total():
    pro = ts.pro_api(TUSHARE_TOKEN)

    current_date = datetime.datetime.now().strftime('%Y%m%d')

    start_date = '20110101'

    while current_date > start_date:
        df = pro.daily(trade_date=current_date)

        file_path = os.path.join(TOTAL_PATH, f'data_{current_date}.csv')

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                line_count = sum(1 for line in file)
                if line_count > 1000:
                    break

        df.to_csv(file_path, index=False)

        print(f'Data for {current_date} saved to {file_path}')

        current_date = (datetime.datetime.strptime(current_date, '%Y%m%d') - datetime.timedelta(days=1)).strftime('%Y%m%d')
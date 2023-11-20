import os
from datetime import datetime

import click
import tushare as ts

from common.common import RESOURCES_PATH, TUSHARE_TOKEN, NORTH_FUNDS_FILE_PATH


@click.command()
def north_funds():
    pro = ts.pro_api(TUSHARE_TOKEN)

    current_date = datetime.now().strftime('%Y%m%d')

    df = pro.moneyflow_hsgt(start_date='19900101', end_date=current_date, limit=10000)

    df.to_csv(NORTH_FUNDS_FILE_PATH, index=False)
import os
from datetime import datetime

import click
import pandas as pd
import tushare as ts

from common.const import NORTH_FUNDS_FILE_PATH, TUSHARE_TOKEN


@click.command()
def north_funds():
    pro = ts.pro_api(TUSHARE_TOKEN)

    current_date = datetime.now().strftime('%Y%m%d')

    df = pro.moneyflow_hsgt(start_date='19900101', end_date=current_date, limit=10000)
    df.set_index('trade_date', inplace=True)

    if os.path.exists(NORTH_FUNDS_FILE_PATH):
        local_df = pd.read_csv(NORTH_FUNDS_FILE_PATH)
        local_df.set_index('trade_date', inplace=True)
        df = pd.concat([local_df, df]).drop_duplicates()

    df = df.reset_index()

    df.to_csv(NORTH_FUNDS_FILE_PATH, index=False)

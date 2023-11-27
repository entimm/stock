import os

import click
import pandas as pd

from common.common import PROCESSED_PATH, RAW_PATH, YEAR
from common.tdx import read_tdx_text, export_data_sort
from common.utils import filter_files_by_date


@click.command()
@click.argument('year', default=YEAR, type=str)
@click.argument('update_n', default=1, type=int)
def convert_astock(year, update_n):
    directory_path = os.path.join(RAW_PATH, '全部Ａ股')
    file_pattern = r'(\d{4})'
    file_pattern = f'全部Ａ股({year}{file_pattern}).txt'

    sort_col_config = {
        ('MA5涨1', False),
        ('MA10涨1', False),
        ('MA20涨1', False),
        ('MA60涨1', False),

        ('MA5跌1', True),
        ('MA10跌1', True),
        ('MA20跌1', True),
        ('MA60跌1', True),
    }

    container = {sort_col: {} for sort_col, _ in sort_col_config}

    file_list = filter_files_by_date(directory_path, file_pattern)
    file_list = sorted(file_list, key=lambda x: x[0], reverse=False)
    if update_n:
        file_list = file_list[-update_n::]

    for file_path, date in file_list:
        df = read_tdx_text(file_path)
        for sort_col, is_asc in sort_col_config:
            container[sort_col][date] = export_data_sort(df, sort_col, is_asc, 100)

    for sort_col, data in container.items():
        csv_file = os.path.join(PROCESSED_PATH, f'{year}-{sort_col}.csv')
        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            df = pd.DataFrame()

        df = pd.concat([df, pd.DataFrame(data)], axis=1)
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.reindex(sorted(df.columns), axis=1)
        df.to_csv(csv_file, index=False)

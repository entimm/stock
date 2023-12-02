import os

import click
import numpy as np
import pandas as pd

from common.common import PROCESSED_PATH, RAW_V2_PATH, YEAR
from common.tdx import read_tdx_text, export_data_sort
from common.utils import filter_files_by_date


def process_data(file_list, export_columns, output_filename):
    container = {}

    for file_path, date in file_list:
        df = read_tdx_text(file_path)
        container[date] = np.hstack((
            export_data_sort(df, *export_columns[0]),
            np.array(['']),
            export_data_sort(df, *export_columns[1]),
            np.array(['']),
            export_data_sort(df, *export_columns[2]),
            np.array(['']),
            export_data_sort(df, *export_columns[3]),
        ))

    df = pd.DataFrame(container)
    df = df.reindex(sorted(df.columns), axis=1)
    df.to_csv(os.path.join(PROCESSED_PATH, output_filename), index=False)


def get_file_list(year):
    directory_path = os.path.join(RAW_V2_PATH, '行业概念')
    file_pattern = r'(\d{4})'
    file_pattern = f'行业概念({year}{file_pattern}).txt'

    file_list = filter_files_by_date(directory_path, file_pattern)

    return sorted(file_list, key=lambda x: x[0], reverse=False)


@click.command()
@click.argument('year', default=YEAR, type=str)
def convert_gnbk(year):
    export_columns = [
        ('超短强度', False, 20),
        ('强度评分', False, 20),
        ('超短强度', True, 20),
        ('强度评分', True, 20),
    ]

    process_data(get_file_list(year), export_columns, f'GNBK-ANGLE{year}.csv')


@click.command()
@click.argument('year', default=YEAR, type=str)
def convert_gnbk_trend_up(year):
    export_columns = [
        ('MA5涨1', False, 20),
        ('MA10涨1', False, 20),
        ('MA20涨1', False, 20),
        ('MA60涨1', False, 20),
    ]

    process_data(get_file_list(year), export_columns, f'GNBK-TREND-UP{year}.csv')


@click.command()
@click.argument('year', default=YEAR, type=str)
def convert_gnbk_trend_down(year):
    export_columns = [
        ('MA5跌1', True, 20),
        ('MA10跌1', True, 20),
        ('MA20跌1', True, 20),
        ('MA60跌1', True, 20),
    ]

    process_data(get_file_list(year), export_columns, f'GNBK-TREND-DOWN{year}.csv')

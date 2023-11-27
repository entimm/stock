import os

import click
import numpy as np
import pandas as pd

from common.common import PROCESSED_PATH, RAW_PATH, YEAR
from common.tdx import read_tdx_text, export_data_sort
from common.utils import filter_files_by_date


@click.command()
@click.argument('year', default=YEAR, type=str)
def convert_gnbk(year):
    directory_path = os.path.join(RAW_PATH, '行业概念')
    file_pattern = r'(\d{4})'
    file_pattern = f'行业概念({year}{file_pattern}).txt'

    container = {}

    file_list = filter_files_by_date(directory_path, file_pattern)
    file_list = sorted(file_list, key=lambda x: x[0], reverse=False)
    for file_path, date in file_list:
        df = read_tdx_text(file_path)
        container[date] = np.hstack((
            export_data_sort(df, '超短强度', False, 20),
            np.array(['']),
            export_data_sort(df, '强度评分', False, 20),
            np.array(['']),
            export_data_sort(df, '超短强度', True, 20),
            np.array(['']),
            export_data_sort(df, '强度评分', True, 20),
        ))

    df = pd.DataFrame(container)
    df = df.reindex(sorted(df.columns), axis=1)
    df.to_csv(os.path.join(PROCESSED_PATH, f'GNBK{year}.csv'), index=False)

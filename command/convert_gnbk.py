import argparse
import datetime
import os
import re

import numpy as np
import pandas as pd

import root
from common.utils import read_tdx_text, filter_files_by_date


def sort(df, col, asc):
    top_20 = df.sort_values(by=col, ascending=asc).head(20)
    top_20 = top_20['名称'].astype(str) + '|' + top_20['涨幅%'].astype(str) + '|' + top_20[col].astype(str)

    return top_20.values


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='转换处理概念板块')
    current_year = datetime.datetime.now().year
    parser.add_argument('year', type=int, nargs='?', default=current_year)
    args = parser.parse_args()

    year = args.year

    directory_path = f"{root.path}/resources/raw/行业概念"
    file_pattern = r'(\d{4})'
    file_pattern = f'行业概念({year}{file_pattern}).txt'

    sort_col_config = [
        '超短强度',
        '强度评分',
    ]

    container = {}

    file_list = filter_files_by_date(directory_path, file_pattern)
    file_list = sorted(file_list, key=lambda x: x[0], reverse=False)
    for file_path, date in file_list:
        df = read_tdx_text(file_path)
        for sort_col in sort_col_config:
            container[date] = np.hstack((
                sort(df, '超短强度', False),
                np.array(['']),
                sort(df, '强度评分', False),
                np.array(['']),
                sort(df, '超短强度', True),
                np.array(['']),
                sort(df, '强度评分', True),
            ))

    df = pd.DataFrame(container)
    df = df.reindex(sorted(df.columns), axis=1)
    df.to_csv(f"{root.path}/resources/new_processed/GNBK{year}.csv", index=False)

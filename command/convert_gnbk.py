import argparse
import datetime
import os
import re

import numpy as np
import pandas as pd

import root


def filter_files_by_date(directory, file_pattern):
    file_regex = re.compile(file_pattern)

    for root, dirs, files in os.walk(directory):
        for file in files:
            match = file_regex.match(file)
            if match:
                yield os.path.join(root, file), match.group(1)


def read_csv(file_path):
    df = pd.read_csv(file_path, header=1, skipfooter=1, engine='python', encoding='gbk', sep='\t', index_col=None,
                     dtype={0: str}, skipinitialspace=True)

    df.columns = df.columns.str.strip()
    df = df.iloc[:, :-1]
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)

    return df


def sort(df, col, asc):
    top_20 = df.sort_values(by=col, ascending=asc).head(20)
    top_20 = top_20['名称'].astype(str) + '|' + top_20['涨幅%'].astype(str) + '|' + top_20[col].astype(str)

    return top_20.values


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='转换处理A股')
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

    file_iter = filter_files_by_date(directory_path, file_pattern)
    for file_path, date in file_iter:
        df = read_csv(file_path)
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

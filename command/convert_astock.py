import argparse
import datetime
import os
import re

import pandas as pd

import root


def filter_files_by_date(directory, file_pattern):
    file_regex = re.compile(file_pattern)

    list = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            match = file_regex.match(file)
            if match:
                list.append((os.path.join(root, file), match.group(1)))

    return list


def read_tdx_text(file_path):
    df = pd.read_csv(file_path, header=1, skipfooter=1, engine='python', encoding='gbk', sep='\t', index_col=None,
                     dtype={0: str}, skipinitialspace=True)

    df.columns = df.columns.str.strip()
    df = df.iloc[:, :-1]
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)

    return df


def sort(df, col, asc):
    top_100 = df.sort_values(by=col, ascending=asc).head(100)
    top_100 = top_100['代码'].astype(str) + '|' + top_100['涨幅%'].astype(str) + '|' + top_100[col].astype(str)

    return top_100.values


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='转换处理A股')
    current_year = datetime.datetime.now().year
    parser.add_argument('year', type=int, nargs='?', default=current_year)
    parser.add_argument('update_n', type=int, nargs='?', default=0)

    args = parser.parse_args()

    year = args.year
    update_n = args.update_n

    directory_path = f"{root.path}/resources/raw/全部Ａ股"
    file_pattern = r'(\d{4})'
    file_pattern = f'全部Ａ股({year}{file_pattern}).txt'

    sort_col_config = {
        'MA5涨1': False,
        'MA10涨1': False,
        'MA20涨1': False,
        'MA60涨1': False,

        'MA5跌1': True,
        'MA10跌1': True,
        'MA20跌1': True,
        'MA60跌1': True,
    }

    container = {sort_col: {} for sort_col in sort_col_config}

    file_list = filter_files_by_date(directory_path, file_pattern)
    file_list = sorted(file_list, key=lambda x: x[0], reverse=False)
    if update_n:
        file_list = file_list[-update_n::]

    for file_path, date in file_list:
        df = read_tdx_text(file_path)
        for sort_col, is_asc in sort_col_config.items():
            container[sort_col][date] = sort(df, sort_col, is_asc)

    for sort_col, data in container.items():
        csv_file = f"{root.path}/resources/new_processed/{year}-{sort_col}.csv"
        try:
            df = pd.read_csv(csv_file)
            print(df)
        except FileNotFoundError:
            df = pd.DataFrame()

        df = pd.concat([df, pd.DataFrame(data)], axis=1)
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.reindex(sorted(df.columns), axis=1)
        df.to_csv(csv_file, index=False)

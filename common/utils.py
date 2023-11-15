import os
import re

import pandas as pd


def read_tdx_text(file_path):
    df = pd.read_csv(file_path, header=1, skipfooter=1, engine='python', encoding='gbk', sep='\t', index_col=None,
                     dtype={0: str}, skipinitialspace=True)

    df.columns = df.columns.str.strip()
    df = df.iloc[:, :-1]
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)

    return df


def filter_files_by_date(directory, file_pattern):
    file_regex = re.compile(file_pattern)

    list = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            match = file_regex.match(file)
            if match:
                list.append((os.path.join(root, file), match.group(1)))

    return list

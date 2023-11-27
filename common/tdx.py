import os
from pathlib import Path

import pandas as pd

from common.common import TDX_BLOCK_NEW_PATH


def read_tdx_text(file_path):
    df = pd.read_csv(file_path, header=1, skipfooter=1, engine='python', encoding='gbk', sep='\t', index_col=None, dtype={0: str}, skipinitialspace=True)

    df.columns = df.columns.str.strip()
    df = df.iloc[:, :-1]
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)

    return df


def read_bk(bk_key):
    zxg_file = os.path.join(TDX_BLOCK_NEW_PATH, f'{bk_key}.blk')

    if not Path(zxg_file).exists():
        raise Exception("file not exists")

    codes = open(zxg_file).read().splitlines()

    return [c[1:] for c in codes if c != ""]


def export_data_sort(df, col, asc, num):
    top = df.sort_values(by=col, ascending=asc).head(num)
    top = top['代码'].astype(str) + '|' + top['涨幅%'].astype(str) + '|' + top[col].astype(str)

    return top.values
import os
from pathlib import Path

import pandas as pd

from common.const import TDX_BLOCK_NEW_PATH, TDX_STOCK_INFO_FILE_PATH


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


stock_info_df = read_tdx_text(TDX_STOCK_INFO_FILE_PATH)
stock_info_df.set_index('代码', inplace=True)

stock_info_df['主营业务'] = stock_info_df['主营业务'].astype(str).fillna('')
stock_info_df['主题投资'] = stock_info_df['主题投资'].astype(str).fillna('')
stock_info_df['公司亮点'] = stock_info_df['公司亮点'].astype(str).fillna('')
stock_info_df['名称'] = stock_info_df['名称'].astype(str).fillna('')
stock_info_df['地域'] = stock_info_df['地域'].astype(str).fillna('')
stock_info_df['概念'] = stock_info_df['概念'].astype(str).fillna('')
stock_info_df['流通市值'] = stock_info_df['流通市值'].astype(str).fillna('')
stock_info_df['自定义'] = stock_info_df['自定义'].astype(str).fillna('')
stock_info_df['行业'] = stock_info_df['行业'].astype(str).fillna('')
stock_info_df['风格'] = stock_info_df['风格'].astype(str).fillna('')

stock_info_df = stock_info_df.drop(['涨幅%', '收盘', '总金额',], axis=1)

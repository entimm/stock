import click
import numpy as np
import pandas as pd


def calculate_bars_last_count(condition):
    rt = np.zeros(len(condition) + 1, dtype=int)
    for i in range(len(condition)):
        rt[i + 1] = rt[i] + 1 if condition[i] else rt[i + 1]
    return rt[1:]


@click.command()
@click.argument('ticker', type=str)
def cal_trend_ptg(ticker):
    df = pd.read_csv(f'kline/{ticker}-d.csv')

    # 计算超短强度指标
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['超短强度'] = np.arctan((df['ma5'] / df['ma5'].shift(1) - 1) * 100) * 57.3

    condition = df['超短强度'] >= 0
    df['符合条件交易日'] = calculate_bars_last_count(condition)

    # def calculate_start_price(row):
    #     index = row.name - row['符合条件交易日']
    #     return df.loc[index, 'close'] if row['符合条件交易日'] > 0 else None
    # df['基准价格'] = df.apply(calculate_start_price, axis=1)

    def calculate_start_price(df):
        index = df.index - df['符合条件交易日']
        return df.loc[index, 'close'].values

    df['基准价格'] = calculate_start_price(df)

    df['趋势涨幅'] = (df['close'] / df['基准价格'] - 1) * 100

    print(df.tail(50))

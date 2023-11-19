import numpy as np


def _bars_last_count(condition):
    rt = np.zeros(len(condition) + 1, dtype=int)
    for i in range(len(condition)):
        rt[i + 1] = rt[i] + 1 if condition[i] else rt[i + 1]
    return rt[1:]


def _ma_trend_base_price1(df):
    index = df.index - df['match_k_num']
    return df.loc[index, 'close'].values


def _ma_trend_base_price2(df):
    def _map_process(row):
        index = row.name - row['match_k_num']
        return df.loc[index, 'close'] if row['match_k_num'] > 0 else None

    return df.apply(_map_process, axis=1)


def ma(df, window):
    return df['close'].rolling(window=window).mean()


def ma_angle(df, ma_field):
    return np.arctan((df[ma_field] / df[ma_field].shift(1) - 1) * 100) * 57.3


def ma_trend(df, condition):
    df['match_k_num'] = _bars_last_count(condition)
    df['ma_trend_base_price'] = _ma_trend_base_price1(df)

    return (df['close'] / df['ma_trend_base_price'] - 1) * 100

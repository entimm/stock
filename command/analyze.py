import click
import numpy as np
from mootdx.reader import Reader

from common.common import TDX_DIR

reader = Reader.factory(market='std', tdxdir=TDX_DIR)


def cal_ma(df, window):
    ma = f'ma{window}'
    df[ma] = df['close'].rolling(window=window).mean()

    df[f'{ma}_angle'] = np.arctan((df[ma].diff() / df[ma].shift(1)) * 100) * 57.3


def cal_pct_change(df):
    df['pct_change'] = ((df['close'] - df['close'].shift(1)) / df['close'].shift(1)) * 100


@click.command()
@click.argument('symbol', type=str)
def analyze(symbol):
    df_5i = reader.fzline(symbol=symbol)
    cal_ma(df_5i, 5)
    cal_ma(df_5i, 10)
    cal_ma(df_5i, 20)
    cal_ma(df_5i, 60)
    cal_ma(df_5i, 240)
    cal_ma(df_5i, 480)
    cal_ma(df_5i, 960)

    cal_pct_change(df_5i)

    print(df_5i.tail(20))

    df_d = reader.daily(symbol=symbol)
    cal_ma(df_d, 5)
    cal_ma(df_d, 10)
    cal_ma(df_d, 20)
    cal_ma(df_d, 60)
    cal_ma(df_d, 240)

    cal_pct_change(df_d)

    print(df_d.tail(20))

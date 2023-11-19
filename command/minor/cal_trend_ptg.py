import click
from mootdx.reader import Reader

from common.common import TDX_DIR
from common.price_calculate import ma_trend, ma, ma_angle

reader = Reader.factory(market='std', tdxdir=TDX_DIR)


@click.command()
@click.argument('ticker', type=str)
def cal_trend_ptg(ticker):
    df = reader.daily(symbol=ticker)
    df = df.reset_index()

    df['ma5'] = ma(df, 5)
    df['ma_angle'] = ma_angle(df, 'ma5')
    df['ma5_trend'] = ma_trend(df, df['ma_angle'] >= 0)

    print(df.tail(50))

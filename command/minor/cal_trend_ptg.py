import click

from common.data import local_tdx_reader
from common.price_calculate import ma_trend, ma, ma_angle


@click.command()
@click.argument('ticker', type=str)
def cal_trend_ptg(ticker):
    df = local_tdx_reader.daily(symbol=ticker)
    df = df.reset_index()

    df['ma5'] = ma(df, 5)
    df['ma_angle'] = ma_angle(df, 'ma5')
    df['ma5_trend'] = ma_trend(df, df['ma_angle'] >= 0)

    print(df.tail(50))

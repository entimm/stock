import click

from common.price_calculate import ma_trend, ma, ma_angle
from common.quotes import fetch_local_daily


@click.command()
@click.argument('ticker', type=str)
def cal_trend_ptg(ticker):
    df = fetch_local_daily(ticker)
    df = df.reset_index()

    df['ma5'] = ma(df, 5)
    df['ma_angle'] = ma_angle(df, 'ma5')
    df['ma5_trend'] = ma_trend(df, df['ma_angle'] >= 0)

    print(df.tail(50))

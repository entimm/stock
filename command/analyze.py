import click
from prettytable import PrettyTable

from common import price_calculate
from common.common import PeriodEnum
from common.utils import realtime_whole_df

MA_CONFIG_LIST = {
    'ma5': {
        'window': 5,
        'type': 'short',
    }, 'ma10': {
        'window': 10,
        'type': 'short',
    }, 'ma20': {
        'window': 20,
        'type': 'short',
    }, 'ma60': {
        'window': 60,
        'type': 'standard',
    }, 'ma240': {
        'window': 240,
        'type': 'long',
    }, 'ma480': {
        'window': 480,
        'type': 'long',
    }, 'ma960': {
        'window': 960,
        'type': 'long',
    }}


def cal(df):
    df['open'] = round(df['open'], 3)
    df['high'] = round(df['high'], 3)
    df['low'] = round(df['low'], 3)
    df['close'] = round(df['close'], 3)

    for ma_field, ma_config in MA_CONFIG_LIST.items():
        df[ma_field] = round(price_calculate.ma(df, ma_config['window']), 3)
        df[f'{ma_field}_angle'] = round(price_calculate.ma_angle(df, ma_field), 3)
        df[f'{ma_field}_diff'] = round((df['close'] / df[ma_field] - 1) * 100, 3)
        df[f'{ma_field}_high_diff'] = round((df['high'] / df[ma_field] - 1) * 100, 3)
        df[f'{ma_field}_low_diff'] = round((df['low'] / df[ma_field] - 1) * 100, 3)

    latest_row = df.iloc[-1]
    table = PrettyTable()
    table.field_names = ["均线", "方向", "差值", "high差值", "low差值"]
    for ma_field, ma_config in MA_CONFIG_LIST.items():
        table.add_row([
            ma_field,
            latest_row[f'{ma_field}_angle'],
            latest_row[f'{ma_field}_diff'],
            latest_row[f'{ma_field}_high_diff'],
            latest_row[f'{ma_field}_low_diff'],
        ], divider=True)

    click.echo(table)


@click.command()
@click.argument('symbol', type=str)
def analyze(symbol):
    df_5f = realtime_whole_df(symbol, PeriodEnum.F5)
    print('5分钟K')
    cal(df_5f)

    print('日K')
    df_d = realtime_whole_df(symbol, PeriodEnum.D)
    cal(df_d)

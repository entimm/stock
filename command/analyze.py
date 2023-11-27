import click
from rich.console import Console
from rich.table import Table

from common import price_calculate
from common.common import PeriodEnum
from common.quotes import fetch_local_plus_real

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


def cal(df, title):
    df = df.round({'open': 3, 'high': 3, 'low': 3, 'close': 3})

    for ma_field, ma_config in MA_CONFIG_LIST.items():
        ma_values = price_calculate.ma(df, ma_config['window'])
        df[ma_field] = round(ma_values, 3)
        df[f'{ma_field}_angle'] = round(price_calculate.ma_angle(df, ma_field), 3)
        df[f'{ma_field}_diff'] = round((df['close'] / ma_values - 1) * 100, 3)
        df[f'{ma_field}_high_diff'] = round((df['high'] / ma_values - 1) * 100, 3)
        df[f'{ma_field}_low_diff'] = round((df['low'] / ma_values - 1) * 100, 3)

    latest_row = df.iloc[-1]

    fields = ["均线", "方向", "差值", "high差值", "low差值"]
    table = Table(*fields, title=title, show_header=True, header_style="bold magenta")
    for ma_field, ma_config in MA_CONFIG_LIST.items():
        table.add_row(
            f"{ma_field}",
            f"{latest_row[f'{ma_field}_angle']}",
            f"{latest_row[f'{ma_field}_diff']}",
            f"{latest_row[f'{ma_field}_high_diff']}",
            f"{latest_row[f'{ma_field}_low_diff']}"
        )

    console = Console()
    console.print(table)


@click.command()
@click.argument('symbol', type=str)
def analyze(symbol):
    df_5f = fetch_local_plus_real(symbol, PeriodEnum.F5)
    cal(df_5f, '5分钟K')

    df_d = fetch_local_plus_real(symbol, PeriodEnum.D)
    cal(df_d, '日K')

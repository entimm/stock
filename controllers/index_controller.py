import datetime
import math
from enum import Enum, auto

import pandas as pd
from flask import render_template, Blueprint, request, url_for, redirect

from mootdx.quotes import Quotes
from mootdx.reader import Reader

from logger import logger

blueprint = Blueprint('index', __name__)

TDX_DIR = '/Volumes/[C] Windows 11/Apps/通达信金融终端(开心果整合版)V2023.03'

FREQUENCY_MINUTE = 8
FREQUENCY_FIVE_MINUTES = 0
FREQUENCY_DAILY = 9


def minutes_since_open():
    now = datetime.datetime.now()
    target = datetime.datetime(now.year, now.month, now.day, 9, 30)
    diff = now - target
    return math.ceil(diff.total_seconds() / 60)


class PeriodEnum(Enum):
    F1 = auto()
    F5 = auto()
    D = auto()


def initialize_tdx():
    try:
        reader = Reader.factory(market='std', tdxdir=TDX_DIR)
        client = Quotes.factory(market='std')
        return reader, client
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        return None, None


def row_to_kline(row):
    return {
        'timestamp': row.name.strftime("%Y-%m-%d %H:%M:%S"),
        'open': row['open'],
        'high': row['high'],
        'low': row['low'],
        'close': row['close'],
        'amount': row['amount'],
        'volume': row['volume'],
    }


def generate_kline_list(df):
    return [row_to_kline(row) for _, row in df.iterrows()]


@blueprint.route('/')
def index():
    symbol = request.args.get('symbol', '', type=str)
    period = request.args.get('period', '', type=str)

    if not symbol or not period:
        target_url = url_for('index.index', symbol='600519', period=PeriodEnum.F5.name)
        return redirect(target_url)

    # 初始化 TDX
    reader, client = initialize_tdx()

    if reader is None or client is None:
        return render_template('error.html', error_message='Failed to initialize TDX.')

    if period == PeriodEnum.F1.name:
        df = reader.minute(symbol=symbol)
        real_time_df = client.bars(symbol=symbol, frequency=FREQUENCY_MINUTE, offset=minutes_since_open())
    elif period == PeriodEnum.F5.name:
        df = reader.fzline(symbol=symbol)
        real_time_df = client.bars(symbol=symbol, frequency=FREQUENCY_FIVE_MINUTES, offset=math.ceil(minutes_since_open() / 5.0))
    else:
        df = reader.daily(symbol=symbol)
        real_time_df = client.bars(symbol=symbol, frequency=FREQUENCY_DAILY, offset=1)

    df = pd.concat([df, pd.DataFrame(real_time_df)], axis=0)

    kline_list = generate_kline_list(df)

    return render_template('index.html', kline_list=kline_list)

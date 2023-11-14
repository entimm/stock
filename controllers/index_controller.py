import datetime
import math
from enum import Enum, auto

import pandas as pd
from flask import render_template, Blueprint, request, url_for, redirect
from mootdx.quotes import Quotes
from mootdx.reader import Reader

blueprint = Blueprint('index', __name__)

TDX_DIR = '/Volumes/[C] Windows 11/Apps/通达信金融终端(开心果整合版)V2023.03'


class PeriodEnum(Enum):
    F1 = auto()
    F5 = auto()
    D = auto()


FREQUENCY_MAP = {
    PeriodEnum.F1: 8,
    PeriodEnum.F5: 0,
    PeriodEnum.D: 9
}


def minutes_since_open():
    now = datetime.datetime.now()
    target = datetime.datetime(now.year, now.month, now.day, 9, 30)
    diff = now - target
    return math.ceil(diff.total_seconds() / 60)


def fetch_local_data(reader, symbol, period):
    if period == PeriodEnum.F1:
        return reader.minute(symbol=symbol)
    elif period == PeriodEnum.F5:
        return reader.fzline(symbol=symbol)
    elif period == PeriodEnum.D:
        return reader.daily(symbol=symbol)


def cal_real_offset(period):
    minutes = minutes_since_open()
    if period == PeriodEnum.F1:
        return minutes
    elif period == PeriodEnum.F5:
        return math.ceil(minutes)
    elif period == PeriodEnum.D:
        return 1


@blueprint.route('/')
def index():
    symbol = request.args.get('symbol', '', type=str)
    period = request.args.get('period', '', type=str).upper()

    if not symbol or not period:
        return redirect(url_for('index.index', symbol='600519', period=PeriodEnum.F5.name))

    reader = Reader.factory(market='std', tdxdir=TDX_DIR)
    client = Quotes.factory(market='std')

    period_enum = PeriodEnum[period]
    frequency = FREQUENCY_MAP.get(period_enum)

    local_df = fetch_local_data(reader, symbol, period_enum)
    real_time_df = client.bars(symbol=symbol, frequency=frequency, offset=cal_real_offset(period_enum))

    df = pd.concat([local_df, pd.DataFrame(real_time_df)], axis=0)
    kline_list = df.apply(row_to_kline, axis=1).to_list()

    template_var = {
        'symbol': symbol,
        'period': period,
        'kline_list': kline_list,
        'period_list': {
            PeriodEnum.F1.name: '1分钟',
            PeriodEnum.F5.name: '5分钟',
            PeriodEnum.D.name: '天',
        },
    }

    return render_template('index.html', **template_var)


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

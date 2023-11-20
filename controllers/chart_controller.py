import datetime
import math
from enum import Enum, auto

import pandas as pd
from flask import render_template, Blueprint, request, url_for, redirect
from mootdx.quotes import Quotes

from common.data import symbol_name_dict, gnbk_dict, local_tdx_reader

blueprint = Blueprint('chart', __name__)


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


@blueprint.route('/chart')
def index():
    symbol = request.args.get('symbol', '', type=str)
    period = request.args.get('period', '', type=str).upper()
    req_real = request.args.get('req_real', 0, type=int)

    if not symbol or not period:
        return redirect(url_for('index.index', symbol='600519', period=PeriodEnum.F5.name, req_real=0))

    period_enum = PeriodEnum[period]
    frequency = FREQUENCY_MAP.get(period_enum)

    df = fetch_local_data(local_tdx_reader, symbol, period_enum)

    if req_real and period_enum != PeriodEnum.D:
        client = Quotes.factory(market='std')
        real_time_df = client.bars(symbol=symbol, frequency=frequency, offset=cal_real_offset(period_enum))
        df = pd.concat([df, pd.DataFrame(real_time_df)], axis=0)

    kline_list = df.apply(row_to_kline, axis=1).to_list()

    symbol_name = gnbk_dict.get(symbol, symbol) if symbol[0:2] == '88' else symbol_name_dict[symbol]

    template_var = {
        'symbol': symbol,
        'symbol_name': symbol_name,
        'period': period,
        'kline_list': kline_list,
        'period_list': {
            PeriodEnum.F1.name: '1分钟',
            PeriodEnum.F5.name: '5分钟',
            PeriodEnum.D.name: '天',
        },
        'req_real': req_real,
    }

    return render_template('chart.html', **template_var)


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

from flask import render_template, Blueprint, request, url_for, redirect

from common.common import PeriodEnum
from common.utils import realtime_whole_df, symbol_name, symbol_all

blueprint = Blueprint('chart', __name__)


@blueprint.route('/chart')
def chart():
    symbol = request.args.get('symbol', '', type=str)
    period = request.args.get('period', '', type=str).upper()
    req_real = request.args.get('req_real', 0, type=int)

    if not symbol or not period:
        return redirect(url_for('chart.chart', symbol='999999', period=PeriodEnum.D.name, req_real=0))

    period_enum = PeriodEnum[period]
    df = realtime_whole_df(symbol, period_enum)
    kline_list = df.apply(row_to_kline, axis=1).to_list()

    template_var = {
        'symbol': symbol,
        'symbol_name': symbol_name(symbol),
        'period': period,
        'kline_list': kline_list,
        'period_list': {
            PeriodEnum.F1.name: '1分钟',
            PeriodEnum.F5.name: '5分钟',
            PeriodEnum.F15.name: '15分钟',
            PeriodEnum.F30.name: '30分钟',
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
        'volume': row['volume'],
    }


@blueprint.route('/symbol_list')
def symbol_list():
    return {
        'symbol_all_list': symbol_all(),
        'default_show_list': [
            '999999',
            '399006',
            '399001',
            '399300',
            '880003',
            '880878',
            '880879',
        ],
    }

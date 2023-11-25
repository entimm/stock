import json

from chan import chan_config
from chan.chan import Chan
from flask import render_template, Blueprint, request, url_for, redirect
from numpy import bool_

from common.common import PeriodEnum
from common.config import DEFAULT_SELECT_OPTIONS
from common.utils import realtime_whole_df, ticker_name, symbol_all, row_to_kline

blueprint = Blueprint('chart', __name__)


def to_bool(value):
    if isinstance(value, bool_):
        return bool(value)
    return value


@blueprint.route('/chart')
def chart():
    symbol = request.args.get('symbol', '', type=str)
    period = request.args.get('period', '', type=str).upper()
    req_real = request.args.get('req_real', 0, type=int)
    chart_engine = request.args.get('chart_engine', 0, type=int)
    show_chan = request.args.get('show_chan', 0, type=int)

    if not symbol or not period:
        return redirect(url_for('chart.chart', symbol='999999', period=PeriodEnum.D.name, req_real=0))

    period_enum = PeriodEnum[period]
    df = realtime_whole_df(symbol, period_enum, req_real)
    kline_list = df.apply(row_to_kline, axis=1).to_list()

    template_var = {
        'ticker_name': ticker_name(symbol),
        'kline_list': kline_list,
        'period_list': {
            PeriodEnum.F1.name: '1分钟',
            PeriodEnum.F5.name: '5分钟',
            PeriodEnum.F15.name: '15分钟',
            PeriodEnum.F30.name: '30分钟',
            PeriodEnum.D.name: '天',
        },
        'request_args': {
            'symbol': symbol,
            'period': period,
            'req_real': req_real,
            'chart_engine': chart_engine,
            'show_chan': show_chan,
        }
    }

    if show_chan:
        chart_engine = 1
        chan_config.output_text = False
        chan_data = Chan(kline_list).output()
        template_var['chan_data'] = json.dumps(chan_data, default=lambda x: to_bool(x))
        template_var['request_args']['chart_engine'] = chart_engine

    return render_template('chart.html', **template_var)


@blueprint.route('/symbol_list')
def symbol_list():
    return {
        'symbol_all_list': symbol_all(),
        'default_show_list': DEFAULT_SELECT_OPTIONS,
    }

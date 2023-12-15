import json

from chan import chan_config
from chan.chan import Chan
from flask import render_template, Blueprint, request, url_for, redirect
from numpy import bool_
from pypinyin import pinyin, Style

from app_cache import cache
from common.common import PeriodEnum, DEFAULT_SELECT_OPTIONS
from common.config import config
from common.data import limited_up_total_dict
from common.price_calculate import pct_change
from common.quotes import fetch_local_plus_real
from common.tdx import stock_info_df
from common.utils import ticker_name, symbol_all, row_to_kline, start_and_end_in_range
from controllers import make_cache_key

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
    socket_token = request.args.get('socket_token', '', type=str)

    date = request.args.get('date', '', type=str)

    if not symbol or not period:
        return redirect(url_for('chart.chart', symbol='999999', period=PeriodEnum.D.name, req_real=0))

    period_enum = PeriodEnum[period]
    df = fetch_local_plus_real(symbol, period_enum, req_real)
    df['pct_change'] = round(pct_change(df), 2)
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
            'socket_token': socket_token,
            'date': date,
        },
        'indicator_config': config.get('indicator'),
    }

    if date:
        template_var['time_range'] = start_and_end_in_range(kline_list, date)

    if show_chan:
        chart_engine = 1

        tmp_chan_config_keys = ['force_stroke_vertex', 'force_segment_vertex', 'output_union', 'output_fractal', 'stroke_check_break', 'stroke_fix_sure']
        tmp_chan_config = {key: request.args.get(key, None, type=int) for key in tmp_chan_config_keys if request.args.get(key, None, type=int) is not None}
        tmp_chan_config = config['chart']['chan'] | tmp_chan_config

        for key, value in tmp_chan_config.items():
            setattr(chan_config, key, value)

        chan_data = Chan(kline_list).output()
        chan_data['show_ma'] = request.args.get('show_ma', tmp_chan_config['show_ma'], type=int)
        chan_data['show_debug'] = request.args.get('show_debug', tmp_chan_config['show_debug'], type=int)

        template_var['chan_data'] = json.dumps(chan_data, default=lambda x: to_bool(x))
        template_var['request_args']['chart_engine'] = chart_engine

    return render_template('chart.html', **template_var)


@blueprint.route('/symbol_list')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def symbol_list():
    symbol_all_list = symbol_all()
    for item in symbol_all_list:
        item['pinyin'] = ''.join([item[0] for item in pinyin(item['value'], style=Style.FIRST_LETTER)]).upper()

    return {
        'symbol_all_list': symbol_all_list,
        'default_show_list': DEFAULT_SELECT_OPTIONS,
    }


@blueprint.route('/stock_info/<symbol>')
def stock_info(symbol):
    result = {}
    if symbol in stock_info_df.index:
        result = stock_info_df.loc[symbol].to_json()
    return result


@blueprint.route('/limited_up_info/<symbol>')
def limited_up_info(symbol):
    result = dict(limited_up_total_dict.get(symbol, {}))
    if result:
        result['plates_info'] = []
        for item in result.get('plates', []):
            result['plates_info'].append(f"【{item['plate_name']}({item['count']})】{item.get('plate_reason', '')}")

        result.pop('plates', None)

    return result

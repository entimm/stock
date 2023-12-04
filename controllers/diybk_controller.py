from functools import cmp_to_key

from flask import Blueprint, render_template, request

from app_cache import cache
from common import price_calculate
from common.config import config
from common.price_calculate import pct_change
from common.quotes import fetch_latest_daily, fetch_local_daily, local_tdx_reader
from common.quotes import trade_date_list
from common.tdx import read_bk
from common.utils import ticker_name
from controllers import make_cache_key

blueprint = Blueprint('diybk', __name__)


def custom_compare_desc(x, y):
    if x[1] is None or y[1] is None:
        return 1

    return y[1] - x[1]


def custom_compare_asc(x, y):
    if x[1] is None or y[1] is None:
        return 1

    return x[1] - y[1]


@blueprint.route('/diybk')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def diybk():
    df = local_tdx_reader.block_new(group=True)

    bk_key_dict = dict(zip(df['blockname'], df['block_type']))
    bk_key_dict['自选'] = 'zxg'

    bk_code_dict = dict(zip(df['blockname'], df['code_list']))
    for bk_name, symbols_str in bk_code_dict.items():
        bk_code_dict[bk_name] = symbols_str.split(',')

    data = {}

    zxg_dict = {'自选': read_bk('zxg')}
    for item_dict in [zxg_dict, bk_code_dict]:
        for bk_name, symbols in item_dict.items():
            if bk_name in config['diybk']['excluded']:
                continue
            real_price_map = {}
            if bk_name not in config['diybk']['not_real_price']:
                try:
                    real_price_df = fetch_latest_daily(symbols)
                    real_price_df['pct_change'] = round(pct_change(real_price_df), 2)
                    real_price_map = dict(zip(real_price_df['code'], real_price_df['pct_change']))
                except:
                    pass
            for symbol in symbols:
                if len(symbol) > 0:
                    price = real_price_map.get(symbol, '-')
                    data.setdefault(bk_name, []).append(f'{ticker_name(symbol)}|{symbol}|{price}')

    template_var = {
        'data': data,
        'bk_key_dict': bk_key_dict
    }

    return render_template('diybk.html', **template_var)


@blueprint.route('/diybk_history')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def diybk_history():
    ma_config = {'MA5': 5, 'MA10': 10, 'MA20': 20, 'MA60': 60}
    ma_list = list(ma_config.keys())
    ma = request.args.get('ma', ma_list[0])
    ma_v = ma_config[ma]

    direction_list = {
        1: {'name': '涨'},
        2: {'name': '跌'},
    }
    direction = request.args.get('direction', 1, type=int)

    bk_key = request.args.get('bk_key', 'zxg', type=str).upper()
    symbols = read_bk(bk_key)

    stock_data = {}
    for symbol in symbols:
        one_df = fetch_local_daily(symbol=symbol).reset_index().tail(101)

        one_df = one_df.reset_index()

        one_df[ma] = price_calculate.ma(one_df, ma_v)
        one_df[f'{ma}_angle'] = price_calculate.ma_angle(one_df, ma)
        condition = one_df[f'{ma}_angle'] >= 0 if direction == 1 else one_df[f'{ma}_angle'] <= 0
        one_df[f'{ma}_trend'] = price_calculate.ma_trend(one_df, condition)

        one_df['ptc_charge'] = ((one_df['close'] / one_df['close'].shift(1)) - 1) * 100

        stock_data[symbol] = one_df

    result_dict = {}
    for date in trade_date_list.tail(config.get('table_cols', 200))['date'].to_list():
        temp_list = []

        for symbol, stock_df in stock_data.items():
            idx = stock_df[stock_df['date'] == date].index
            if not idx.empty:
                ptc_charge = stock_df.loc[idx, 'ptc_charge'].values[0]
                value = stock_df.loc[idx, f'{ma}_trend'].values[0]
                temp_list.append((f'{ticker_name(symbol)}|{symbol}|{round(ptc_charge, 2)}|{round(value, 2)}', value))

        # 长度不齐就补空白
        temp_list = temp_list + [('-', None)] * (len(symbols) - len(temp_list))

        custom_compare_method = custom_compare_desc if direction == 1 else custom_compare_asc
        sorted_list = [item[0] for item in sorted(temp_list, key=cmp_to_key(custom_compare_method))]

        result_dict[date.strftime('%Y-%m-%d')] = sorted_list

    df = local_tdx_reader.block_new(group=True)
    bk_key_dict = dict(zip(df['blockname'], df['block_type']))
    bk_key_dict = {key: value for key, value in bk_key_dict.items() if key not in config['diybk']['excluded']}
    bk_key_dict['自选'] = 'zxg'

    template_var = {
        'data': dict(reversed(result_dict.items())),
        'ma_list': ma_list,
        'direction_list': direction_list,
        'bk_key_dict': bk_key_dict,
        'request_args': {
            'bk_key': bk_key,
            'ma': ma,
            'direction': direction,
        }
    }

    return render_template('diybk_history.html', **template_var)

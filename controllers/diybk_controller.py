import os
from functools import cmp_to_key
from pathlib import Path

from flask import Blueprint, render_template, request
from mootdx.quotes import Quotes
from mootdx.reader import Reader

from common.common import TDX_DIR
from common.data import symbol_name_dict, gnbk_dict, etf_dict
from common import price_calculate

blueprint = Blueprint('diybk', __name__)


def read_bk(bk_key):
    zxg_file = os.path.join(TDX_DIR, 'T0002', 'blocknew', f'{bk_key}.blk')

    if not Path(zxg_file).exists():
        raise Exception("file not exists")

    codes = open(zxg_file).read().splitlines()

    return [c[1:] for c in codes if c != ""]


def symbol_name(symbol):
    if symbol[0:2] == '88':
        return gnbk_dict.get(symbol, symbol)
    elif symbol[0:2] in ['15', '51', '56', '58']:
        return etf_dict.get(symbol, symbol)
    else:
        return symbol_name_dict[symbol].replace('概念', '')


def custom_compare_desc(x, y):
    if x[1] is None or y[1] is None:
        return 1

    return y[1] - x[1]

def custom_compare_asc(x, y):
    if x[1] is None or y[1] is None:
        return 1

    return x[1] - y[1]


@blueprint.route('/diybk')
def diybk():
    reader = Reader.factory(market='std', tdxdir=TDX_DIR)

    df = reader.block_new(group=True)

    zxg_dict = {'自选': read_bk('zxg')}

    bk_key_dict = dict(zip(df['blockname'], df['block_type']))
    bk_key_dict['自选'] = 'zxg'
    bk_code_dict = dict(zip(df['blockname'], df['code_list']))
    for bk_name, symbols_str in bk_code_dict.items():
        bk_code_dict[bk_name] = symbols_str.split(',')

    client = Quotes.factory(market='std')

    data = {}

    excluded = ['行业概念', '临时']
    for item_dict in [zxg_dict, bk_code_dict]:
        for bk_name, symbols in item_dict.items():
            if bk_name in excluded:
                continue
            real_price_map = {}
            if bk_name not in ['风格', '关键风格']:
                try:
                    real_price_df = client.quotes(symbol=symbols)
                    real_price_df['pct_change'] = round(
                        (real_price_df['price'] / real_price_df['last_close'] - 1) * 100, 2)
                    real_price_map = dict(zip(real_price_df['code'], real_price_df['pct_change']))
                except:
                    pass
            for symbol in symbols:
                if len(symbol) > 0:
                    price = real_price_map.get(symbol, '-')
                    data.setdefault(bk_name, []).append(f'{symbol_name(symbol)}|{symbol}|{price}')

    template_var = {
        'data': data,
        'bk_key_dict': bk_key_dict
    }

    return render_template('diybk.html', **template_var)


@blueprint.route('/diybk_history')
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
    reader = Reader.factory(market='std', tdxdir=TDX_DIR)
    symbols = read_bk(bk_key)

    date_list = reader.daily(symbol='999999').reset_index().tail(100)['date'].to_list()

    stock_data = {}
    for symbol in symbols:
        one_df = reader.daily(symbol=symbol).reset_index().tail(101)

        one_df = one_df.reset_index()

        one_df[ma] = price_calculate.ma(one_df, ma_v)
        one_df[f'{ma}_angle'] = price_calculate.ma_angle(one_df, ma)
        condition = one_df[f'{ma}_angle'] >= 0 if direction == 1 else one_df[f'{ma}_angle'] <= 0
        one_df[f'{ma}_trend'] = price_calculate.ma_trend(one_df, condition)

        one_df['ptc_charge'] = ((one_df['close'] / one_df['close'].shift(1)) - 1) * 100

        stock_data[symbol] = one_df

    result_dict = {}
    for date in date_list:
        temp_list = []

        for symbol, stock_df in stock_data.items():
            idx = stock_df[stock_df['date'] == date].index
            if not idx.empty:
                ptc_charge = stock_df.loc[idx, 'ptc_charge'].values[0]
                value = stock_df.loc[idx, f'{ma}_trend'].values[0]
                temp_list.append((f'{symbol_name(symbol)}|{symbol}|{round(ptc_charge, 2)}|{round(value, 2)}', value))

        temp_list = temp_list + [('-', None)] * (len(symbols) - len(temp_list))

        custom_compare_method = custom_compare_desc if direction == 1 else custom_compare_asc
        sorted_list = [item[0] for item in sorted(temp_list, key=cmp_to_key(custom_compare_method))]

        result_dict[date.strftime('%Y-%m-%d')] = sorted_list

    template_var = {
        'data': dict(reversed(result_dict.items())),
        'bk_key': bk_key,
        'ma_list': ma_list,
        'ma': ma,
        'direction_list': direction_list,
        'direction': direction,
    }

    return render_template('diybk_history.html', **template_var)

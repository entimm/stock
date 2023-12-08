import json
import os
from typing import Dict, List

import pandas as pd
from flask import render_template, request, Blueprint

from app_cache import cache
from common.common import PROCESSED_PATH, YEAR
from common.config import config
from common.data import gnbk_dict, ticker_name_dict
from controllers import make_cache_key

blueprint = Blueprint('table', __name__)


def read_table_data(file_path: str, is_gnbk: bool = False) -> Dict[str, List[str]]:
    result = {}

    df = pd.read_csv(file_path)
    if talbe_cols := config.get('table_cols'):
        df = df.iloc[:, -talbe_cols:]
    for date, row in df.items():
        date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        for col_index, value in enumerate(row):
            if type(value) is str:
                symbol, *rest = value.split('|')
                if is_gnbk:
                    value = '|'.join([gnbk_dict.get(symbol, symbol).replace('概念', ''), symbol, *rest])
                else:
                    value = '|'.join([ticker_name_dict.get(symbol, symbol), symbol, *rest])
            result.setdefault(date, []).append(value)

    result = dict(reversed(result.items()))

    return result


@blueprint.route('/astock_table')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def astock_table():
    ma_list = ['MA5', 'MA10', 'MA20', 'MA60']
    year_list = list(range(YEAR, 2010, -1))

    ma = request.args.get('ma', ma_list[0])
    year = request.args.get('year', year_list[0], type=int)

    direction_list = {
        1: {'name': '涨', 'file': os.path.join(PROCESSED_PATH, f'{year}-{ma}涨1.csv')},
        2: {'name': '跌', 'file': os.path.join(PROCESSED_PATH, f'{year}-{ma}跌1.csv')},
    }

    direction = request.args.get('direction', 1, type=int)
    file_path = direction_list[direction]['file']

    data = read_table_data(file_path)

    template_var = {
        'ma_list': ma_list,
        'year_list': year_list,
        'direction_list': direction_list,
        'data': json.dumps(data, sort_keys=False),
        'request_args': {
            'ma': ma,
            'year': year,
            'direction': direction,
            'socket_token': request.args.get('socket_token', '', str),
        }
    }

    return render_template('astock_table.html', **template_var)


@blueprint.route('/gnbk_table')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def gnbk_table():
    data_type_list = {
        'ANGLE': '强度',
        'TREND-UP': '趋势涨',
        'TREND-DOWN': '趋势跌',
    }
    data_type = request.args.get('data_type', 'ANGLE', type=str)

    year_list = list(range(YEAR, 2017, -1))
    year = request.args.get('year', year_list[0], type=int)

    file_path = os.path.join(PROCESSED_PATH, f'GNBK-{data_type}{year}.csv')

    data = read_table_data(file_path, is_gnbk=True)

    template_var = {
        'year_list': year_list,
        'data_type_list': data_type_list,
        'data': json.dumps(data, sort_keys=False),
        'request_args': {
            'year': year,
            'data_type': data_type,
            'socket_token': request.args.get('socket_token', '', str),
        }
    }

    return render_template('gnbk_table.html', **template_var)

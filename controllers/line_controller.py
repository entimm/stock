import os
from typing import Dict, List

import pandas as pd
from flask import render_template, request, Blueprint

from app_cache import cache
from common.common import PROCESSED_PATH
from common.config import config
from common.data import ticker_name_dict, gnbk_dict
from controllers import make_cache_key

blueprint = Blueprint('line', __name__)


def read_data(file_path: str, row_numbers: List[int], type_val: int = 0, is_gnbk: bool = False) -> Dict[str, Dict[str, List[str]]]:
    result = {'name': {}, 'value': {}}

    df = pd.read_csv(file_path)

    for row_number in row_numbers:
        row = df.loc[row_number - 1 + type_val * 21]

        for date, value in zip(df.columns, row):
            arr = value.split('|')
            name = gnbk_dict.get(arr[0], arr[0]) if is_gnbk else ticker_name_dict.get(arr[0], arr[0])
            result['name'].setdefault(date, []).append(name)
            result['value'].setdefault(date, []).append(arr[2])

    return result


@blueprint.route('/astock')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def astock():
    ma_list = ['MA5', 'MA10', 'MA20', 'MA60']

    year_range = config.get('tdx_processed_astock')
    year_list = list(range(year_range[0], year_range[1] - 1, -1))
    line_list = [
        '1,2,3,4,5,10,20,30,40',
        '1,2,3,4,5,6,7,8,9,10',
        '5,10,15,20,25,30,35,40,45,50',
        '10,20,30,40,50,60,70,80,90,100',
    ]

    ma = request.args.get('ma', ma_list[0])
    year = request.args.get('year', year_list[0], type=int)
    line_id = request.args.get('line_id', 0, type=int)

    direction_list = {
        1: {'name': '涨', 'file': os.path.join(PROCESSED_PATH, f'{year}-{ma}涨1.csv')},
        2: {'name': '跌', 'file': os.path.join(PROCESSED_PATH, f'{year}-{ma}跌1.csv')},
    }

    direction = request.args.get('direction', 1, type=int)
    rows = list(map(int, line_list[line_id].split(',')))
    file_path = direction_list[direction]['file']
    data = read_data(file_path, rows)

    template_var = {
        'ma_list': ma_list,
        'year_list': year_list,
        'line_list': line_list,
        'rows': rows,
        'direction_list': direction_list,
        'data': data,
        'request_args': {
            'ma': ma,
            'year': year,
            'line_id': line_id,
            'direction': direction,
        }
    }

    return render_template('astock.html', **template_var)


@blueprint.route('/gnbk')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def gnbk():
    data_type_list = {
        'ANGLE': {'name': '强度', 'values': ['超短↖', '综合↖', '超短↘', '综合↘']},
        'TREND-UP': {'name': '趋势涨', 'values': ['MA5↖', 'MA10↖', 'MA20↖', 'MA60↖']},
        'TREND-DOWN': {'name': '趋势跌', 'values': ['MA5↘', 'MA10↘', 'MA20↘', 'MA60↘']},
    }
    year_range = config.get('tdx_processed_gnbk')
    year_list = list(range(year_range[0], year_range[1] - 1, -1))
    line_list = [
        '1,2,3,4,5',
        '5,10,15,20',
    ]

    data_type = request.args.get('data_type', 'ANGLE', type=str)
    sub_data_type = request.args.get('sub_data_type', 0, type=int)
    year = request.args.get('year', year_list[0], type=int)
    line_id = request.args.get('line_id', 0, type=int)

    rows = list(map(int, line_list[line_id].split(',')))

    file_path = os.path.join(PROCESSED_PATH, f'GNBK-{data_type}{year}.csv')

    data = read_data(file_path, rows, sub_data_type, True)

    template_var = {
        'year_list': year_list,
        'line_list': line_list,
        'rows': rows,
        'data_type_list': data_type_list,
        'data': data,
        'request_args': {
            'year': year,
            'line_id': line_id,
            'sub_data_type': sub_data_type,
            'data_type': data_type,
        }
    }

    return render_template('gnbk.html', **template_var)

import datetime
import os
from typing import Dict, List

import pandas as pd
from flask import render_template, request, Blueprint

blueprint = Blueprint('line', __name__)

STOCK_META_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'a_stock_meta_list.csv')
GNBK_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'gnbk_list.csv')
PROCESSED_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'new_processed')

YEAR = datetime.datetime.now().year

stock_meta_df = pd.read_csv(STOCK_META_FILE_PATH, dtype={1: str})
symbol_name_dict = dict(zip(stock_meta_df['symbol'], stock_meta_df['name']))

gnbk_df = pd.read_csv(GNBK_FILE_PATH, dtype={0: str})
gnbk_dict = dict(zip(gnbk_df['symbol'], gnbk_df['name']))


def read_data(file_path: str, row_numbers: List[int], type_val: int = 0, is_gnbk: bool = False) -> Dict[str, Dict[str, List[str]]]:
    result = {'name': {}, 'value': {}}

    df = pd.read_csv(file_path)

    for row_number in row_numbers:
        row = df.loc[row_number - 1 + type_val * 21]

        for date, value in zip(df.columns, row):
            arr = value.split('|')
            name = gnbk_dict.get(arr[0], arr[0]) if is_gnbk else symbol_name_dict.get(arr[0], arr[0])
            result['name'].setdefault(date, []).append(name)
            result['value'].setdefault(date, []).append(arr[2])

    return result


@blueprint.route('/astock')
def astock():
    ma_list = ['MA5', 'MA10', 'MA20', 'MA60']
    year_list = list(range(YEAR, 2010, -1))
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
        'ma': ma,
        'year': year,
        'line_id': line_id,
        'direction_list': direction_list,
        'direction': direction,
        'data': data,
    }

    return render_template('astock.html', **template_var)


@blueprint.route('/gnbk')
def gnbk():
    type_list = ['超短↖', '综合↖', '超短↘', '综合↘']
    year_list = list(range(YEAR, 2017, -1))
    line_list = [
        '1,2,3,4,5',
        '5,10,15,20',
    ]

    type_val = request.args.get('type', 0, type=int)
    year = request.args.get('year', year_list[0], type=int)
    line_id = request.args.get('line_id', 0, type=int)

    rows = list(map(int, line_list[line_id].split(',')))

    file_path = os.path.join(PROCESSED_PATH, f'GNBK{year}.csv')

    data = read_data(file_path, rows, type_val, True)

    template_var = {
        'year_list': year_list,
        'line_list': line_list,
        'rows': rows,
        'year': year,
        'line_id': line_id,
        'type_list': type_list,
        'type': type_val,
        'data': data,
    }

    return render_template('gnbk.html', **template_var)

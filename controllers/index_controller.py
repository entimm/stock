import json
import os

import pandas as pd
from flask import render_template, request, Blueprint

import root

blueprint = Blueprint('main', __name__)

strock_meta_df = pd.read_csv(f'{root.path}/resources/a_stock_meta_list.csv', dtype={1: str})
symbol_name_dict = dict(zip(strock_meta_df['symbol'], strock_meta_df['name']))

def read_stock_data(file_path, row_numbers):
    result = {'name': {}, 'value': {}}

    df = pd.read_csv(file_path)

    for row_number in row_numbers:
        row = df.iloc[row_number - 1]

        for col_index, value in enumerate(row):
            date = df.columns[col_index]
            arr = value.split('|')
            result['name'].setdefault(date, []).append(symbol_name_dict.get(arr[0], arr[0]))
            result['value'].setdefault(date, []).append(arr[2])

    return result


def read_gnbk_data(file_path, row_numbers, type_val):
    result = {'name': {}, 'value': {}}

    df = pd.read_csv(file_path)

    for row_number in row_numbers:
        row = df.iloc[row_number - 1 + type_val * 21]

        for col_index, value in enumerate(row):
            date = df.columns[col_index]
            arr = value.split('|')
            result['name'].setdefault(date, []).append(arr[0])
            result['value'].setdefault(date, []).append(arr[2])

    return result


def read_stock_table_data(file_path):
    result = {}

    df = pd.read_csv(file_path)

    data_list = list(df.columns)
    for index, row in df.iterrows():
        for col_index, value in enumerate(row):
            date = data_list[col_index]
            arr = value.split('|')
            arr[0] = symbol_name_dict.get(arr[0], arr[0])
            result.setdefault(f'-{date}-', []).append('|'.join(arr))

    result = dict(reversed(result.items()))

    return result


def read_gnbk_table_data(file_path):
    result = {}

    df = pd.read_csv(file_path)

    data_list = list(df.columns)
    for index, row in df.iterrows():
        for col_index, value in enumerate(row):
            date = data_list[col_index]
            if type(value) is str:
                value = value.replace('概念', '')
            result.setdefault(f'-{date}-', []).append(value)

    result = dict(reversed(result.items()))

    return result


@blueprint.route('/astock')
def astock():
    ma_list = ['MA5', 'MA10', 'MA20', 'MA60']
    year_list = list(range(2023, 2010, -1))
    line_list = [
        '1,2,3,4,5,10,20,30,40',
        '1,2,3,4,5,6,7,8,9,10',
        '5,10,15,20,25,30,35,40,45,50',
        '10,20,30,40,50,60,70,80,90,100',
    ]

    ma = request.args.get('ma', ma_list[0])
    year = request.args.get('year', year_list[0], type=int)
    line_id = int(request.args.get('line_id', 0))

    path = f"{root.path}/resources/new_processed/"
    direction_list = {
        1: {'name': '涨', 'file': f'{path}{year}-{ma}涨1.csv'},
        2: {'name': '跌', 'file': f'{path}{year}-{ma}跌1.csv'},
    }

    direction = request.args.get('direction', 1, type=int)
    direction = int(direction)

    rows = list(map(int, line_list[line_id].split(',')))
    file_path = direction_list[direction]['file']
    data = read_stock_data(file_path, rows)

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


@blueprint.route('/astock_table')
def astock_table():
    ma_list = ['MA5', 'MA10', 'MA20', 'MA60']
    year_list = list(range(2023, 2010, -1))

    ma = request.args.get('ma', ma_list[0])
    year = request.args.get('year', year_list[0], type=int)

    path = f"{root.path}/resources/new_processed/"
    direction_list = {
        1: {'name': '涨', 'file': f'{path}{year}-{ma}涨1.csv'},
        2: {'name': '跌', 'file': f'{path}{year}-{ma}跌1.csv'},
    }

    direction = request.args.get('direction', 1, type=int)
    direction = int(direction)

    file_path = direction_list[direction]['file']

    data = read_stock_table_data(file_path)

    template_var = {
        'ma_list': ma_list,
        'year_list': year_list,
        'ma': ma,
        'year': year,
        'direction_list': direction_list,
        'direction': direction,
        'data': json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False),
    }

    return render_template('astock_table.html', **template_var)


@blueprint.route('/gnbk')
def gnbk():
    type_list = ['超短↖', '综合↖', '超短↘', '综合↘']
    year_list = list(range(2023, 2017, -1))
    line_list = [
        '1,2,3,4,5',
        '5,10,15,20',
    ]

    type_val = request.args.get('type', 0, type=int)
    year = request.args.get('year', year_list[0], type=int)
    line_id = int(request.args.get('line_id', 0))

    rows = list(map(int, line_list[line_id].split(',')))

    file_path = os.path.join(f'{root.path}/resources/new_processed/', f"GNBK{year}.csv")

    data = read_gnbk_data(file_path, rows, type_val)

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


@blueprint.route('/gnbk_table')
def gnbk_table():
    year_list = list(range(2023, 2017, -1))
    year = request.args.get('year', year_list[0], type=int)

    file_path = os.path.join(f'{root.path}/resources/new_processed/', f"GNBK{year}.csv")

    data = read_gnbk_table_data(file_path)

    template_var = {
        'year_list': year_list,
        'year': year,
        'data': json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False),
    }

    return render_template('gnbk_table.html', **template_var)



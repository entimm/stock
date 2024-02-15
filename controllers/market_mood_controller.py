import os
from datetime import datetime

import pandas as pd
from flask import Blueprint, jsonify, render_template, request

from app_cache import cache
from common.const import RESOURCES_PATH
from controllers import make_cache_key

blueprint = Blueprint('market_mood', __name__)

field_list = {
    'highest_limit': '最高连板',
    'up_limit_num': '涨停数',
    'down_limit_num': '跌停数',
    'up_down_limit_rate': '涨跌停比',
    'b1_num': '首板',
    'b2_num': '2板',
    'b3_num': '3板',
    'cont_num1': '2板以上',
    'cont_num2': '3板以上',
    'bn_num': '高度板',
    'p_1t2': '1进2',
    'p_2t3': '2进3',
    'p_3t4': '3进4',
    'today_broke_ptg': '今日炸板率',
    'yesterday_limit_up_cptg': '昨日涨停表现',
    'yesterday_constant_cptg': '昨日连板表现',
    'yesterday_broke_cptg': '昨日破板表现',
    'strong': '强度',
    'st_down_limit_num': 'st跌停数',
    'st_up_limit_num': 'st涨停数',
    'st_up_down_limit_rate': 'st涨跌停比',
    'big_noodle': '大面',
    'up_num': '上涨家数',
    'down_num': '下跌家数',
    'up_down_rate': '涨跌比',
    'total_amount': '总成交额',
}


@blueprint.route('/market_mood')
def market_mood():
    field = request.args.get('field', 'highest_limit', type=str)

    return render_template('market_mood.html', **{
        'field_list': field_list,
        'request_args': {
            'field': field,
        }
    })


@blueprint.route('/market_mood_data')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def market_mood_data():
    file_path = os.path.join(RESOURCES_PATH, f'kaipanla.csv')
    df = pd.read_csv(file_path)

    df['cont_num1'] = df['b2_num'] + df['b3_num'] + df['bn_num']
    df['cont_num2'] = df['b3_num'] + df['bn_num']

    df['up_down_limit_rate'] = round(df['up_limit_num'] / (df['up_limit_num'] + df['down_limit_num']) * 100, 2)
    df['st_up_down_limit_rate'] = round(df['st_up_limit_num'] / (df['st_up_limit_num'] + df['st_down_limit_num']) * 100, 2)
    df['up_down_rate'] = round(df['up_num'] / (df['up_num'] + df['down_num']) * 100, 2)

    field = request.args.get('field', 'highest_limit', type=str)

    chart_data = df[['date', field]].tail(300).to_dict(orient='records')

    return jsonify(chart_data)


@blueprint.route('/market_mood_table')
def market_mood_table():
    year_list = list(range(datetime.now().year, 2018, -1))
    year = request.args.get('year', datetime.now().year, type=int)

    file_path = os.path.join(RESOURCES_PATH, f'kaipanla.csv')
    df = pd.read_csv(file_path, parse_dates=['date'])
    if year == datetime.now().year:
        df = df.tail(300)
    else:
        df = df[df['date'].dt.year == year]

    df['cont_num1'] = df['b2_num'] + df['b3_num'] + df['bn_num']
    df['cont_num2'] = df['b3_num'] + df['bn_num']

    df['up_down_limit_rate'] = round(df['up_limit_num'] / (df['up_limit_num'] + df['down_limit_num']) * 100, 2)
    df['st_up_down_limit_rate'] = round(df['st_up_limit_num'] / (df['st_up_limit_num'] + df['st_down_limit_num']) * 100, 2)
    df['up_down_rate'] = round(df['up_num'] / (df['up_num'] + df['down_num']) * 100, 2)

    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    table_data = df.tail(300).to_dict(orient='records')

    return render_template('market_mood_table.html', **{
        'field_list': field_list,
        'year_list': year_list,
        'table_data': list(reversed(table_data)),
        'request_args': {
            'year': year,
        }
    })

import os

import pandas as pd
from flask import Blueprint, jsonify, render_template, request

from app_cache import cache
from common.common import RESOURCES_PATH
from controllers import make_cache_key

blueprint = Blueprint('market_mood', __name__)


@blueprint.route('/market_mood')
def market_mood():
    field_list = {
        'highest_limit': '最高连板',
        'big_noodle': '大面',
        'down_limit_num': '跌停数',
        'up_limit_num': '涨停数',
        'st_down_limit_num': 'st跌停数',
        'st_up_limit_num': 'st涨停数',
        'up_num': '上涨家数',
        'down_num': '下跌家数',
        'total_amount': '总成交额',
        'b1_num': '首板',
        'b2_num': '2板',
        'b3_num': '3板',
        'bn_num': '高度板',
        'p_1t2': '1进2',
        'p_2t3': '2进3',
        'p_3t4': '3进4',
        'today_broke_ptg': '今日炸板率',
        'yesterday_limit_up_cptg': '昨日涨停',
        'yesterday_constant_cptg': '昨日连板',
        'yesterday_broke_cptg': '昨日破板',
        'strong': '强度',
    }
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

    field = request.args.get('field', 'highest_limit', type=str)

    chart_data = df[['date', field]].tail(300).to_dict(orient='records')

    return jsonify(chart_data)

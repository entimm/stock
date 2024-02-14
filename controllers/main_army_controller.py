import json
import os
from datetime import datetime

from flask import Blueprint, render_template, request

from app_cache import cache
from common.const import RESOURCES_PATH
from common.utils import ticker_name
from controllers import make_cache_key

blueprint = Blueprint('main_army', __name__)


@blueprint.route('/main_army')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def main_army():
    year_list = list(range(datetime.now().year, 2010, -1))
    year = request.args.get('year', datetime.now().year, type=int)
    direction_list = {
        'up': {'name': '涨'},
        'down': {'name': '跌'},
    }
    direction = request.args.get('direction', 'up', type=str)

    json_file = os.path.join(RESOURCES_PATH, f'main_army_{direction}.json')
    with open(json_file, 'r') as file:
        data_dict = json.load(file)

    if year == datetime.now().year:
        data_dict = {key: data_dict[key] for key in list(data_dict.keys())[-300:]}
    else:
        data_dict = {key: data_dict[key] for key in list(data_dict.keys()) if key[0:4] == str(year)}

    result_dict = {}
    for date, item in data_dict.items():
        for sub_item in item:
            result_dict.setdefault(date, []).append(ticker_name(sub_item['ts_code']) + '|' + sub_item['ts_code'] + '|' + str(sub_item['pct_chg']) + '|' + str(sub_item['amount']))

    template_var = {
        'data': dict(reversed(result_dict.items())),
        'direction_list': direction_list,
        'year_list': year_list,
        'request_args': {
            'socket_token': request.args.get('socket_token', '', str),
            'direction': direction,
            'year': year,
        }
    }

    return render_template('main_army.html', **template_var)

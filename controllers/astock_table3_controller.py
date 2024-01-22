import json
import os

from flask import render_template, request, Blueprint

from app_cache import cache
from common.const import RESOURCES_PATH
from controllers import make_cache_key

blueprint = Blueprint('astock_table3', __name__)


@blueprint.route('/astock_table3')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def astock_table3():
    ma2_data = ma_data('MA2')
    ma3_data = ma_data('MA3')
    ma5_data = ma_data('MA5')
    ma10_data = ma_data('MA10')
    ma20_data = ma_data('MA20')
    ma60_data = ma_data('MA60')

    result_dict = {}
    for key in ma2_data.keys():
        result_dict[key] = ma2_data[key][0:5] + ma3_data[key][0:5] + ma5_data[key][0:5] + ma10_data[key][0:5] + ma20_data[key][0:5] + ma60_data[key][0:5]

    template_var = {
        'data': dict(reversed(result_dict.items())),
        'request_args': {
            'socket_token': request.args.get('socket_token', '', str),
        }
    }

    return render_template('astock_table3.html', **template_var)


def ma_data(ma):
    result_dict = {}
    result_json_file = os.path.join(RESOURCES_PATH, f'{ma}_trend.json')
    if os.path.exists(result_json_file):
        with open(result_json_file, 'r') as file:
            result_dict = json.load(file)

    return {key: result_dict[key][0:10] for key in list(result_dict.keys())[-300:]}

import json
import os

from flask import render_template, request, Blueprint

from app_cache import cache
from common.const import RESOURCES_PATH
from controllers import make_cache_key

blueprint = Blueprint('astock_line2', __name__)


@blueprint.route('/astock_line2')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def astock_table2():
    line_ids = '1,2,3,4,5,6,7,8,9,10'
    rows = list(map(int, line_ids.split(',')))
    ma_list = ['MA2', 'MA3', 'MA5', 'MA10', 'MA20', 'MA60']
    ma = request.args.get('ma', 'MA3')

    result_dict = {}
    result_json_file = os.path.join(RESOURCES_PATH, 'trends', f'{ma}_trend.json')
    if os.path.exists(result_json_file):
        with open(result_json_file, 'r') as file:
            result_dict = json.load(file)

    result_dict = {key: result_dict[key] for key in list(result_dict.keys())[-300:]}

    result = {'name': {}, 'value': {}}

    row_numbers = list(map(int, line_ids.split(',')))

    for date, value in result_dict.items():
        for row_number in row_numbers:
            arr = value[row_number - 1].split('|')
            result['name'].setdefault(date, []).append(arr[0])
            result['value'].setdefault(date, []).append(arr[3])

    template_var = {
        'data': result,
        'rows': rows,
        'ma_list': ma_list,
        'request_args': {
            'ma': ma,
        }
    }

    return render_template('astock_line2.html', **template_var)

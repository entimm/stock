import json
import os

from flask import render_template, request, Blueprint

from app_cache import cache
from common.const import RESOURCES_PATH
from controllers import make_cache_key

blueprint = Blueprint('astock_table2', __name__)


@blueprint.route('/astock_table2')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def astock_table2():
    ma_list = ['MA2', 'MA3', 'MA5']
    ma = request.args.get('ma', 'MA3')

    result_dict = {}
    result_json_file = os.path.join(RESOURCES_PATH, f'{ma}_trend.json')
    if os.path.exists(result_json_file):
        with open(result_json_file, 'r') as file:
            result_dict = json.load(file)

    result_dict = {key: result_dict[key] for key in list(result_dict.keys())[-300:]}

    template_var = {
        'data': dict(reversed(result_dict.items())),
        'ma_list': ma_list,
        'request_args': {
            'socket_token': request.args.get('socket_token', '', str),
            'ma': ma,
        }
    }

    return render_template('astock_table2.html', **template_var)

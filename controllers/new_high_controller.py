import json
import os

from flask import render_template, request, Blueprint

from app_cache import cache
from common.const import RESOURCES_PATH
from controllers import make_cache_key

blueprint = Blueprint('new_high', __name__)


@blueprint.route('/new_high')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def new_high():
    result_dict = {}
    mode = request.args.get('mode', 1, int)
    result_json_file = os.path.join(RESOURCES_PATH, f'new_high.json')
    match mode:
        case 2:
            result_json_file = os.path.join(RESOURCES_PATH, f'new_high_freq60.json')
        case 3:
            result_json_file = os.path.join(RESOURCES_PATH, f'new_high_freq20.json')
    if os.path.exists(result_json_file):
        with open(result_json_file, 'r') as file:
            result_dict = json.load(file)

    result_dict = {key: result_dict[key] for key in list(result_dict.keys())[-300:]}

    mode_list = {1: '强度', 2: '慢频', 3: '快频'}

    template_var = {
        'data': dict(reversed(result_dict.items())),
        'mode_list': mode_list,
        'request_args': {
            'socket_token': request.args.get('socket_token', '', str),
            'mode': mode,
        }
    }

    return render_template('new_high.html', **template_var)

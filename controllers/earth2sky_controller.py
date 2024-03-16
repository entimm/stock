import json
import os

from flask import Blueprint, render_template, request

from common.const import RESOURCES_PATH

blueprint = Blueprint('earth2sky', __name__)

data_type_list = [
    '地天板',
    '天地板',
]


@blueprint.route('/earth2sky_data')
def trade_history_data():
    data_type = request.args.get('data_type', data_type_list[0], type=str)
    result_json_file = os.path.join(RESOURCES_PATH, '', f'{data_type}.json')
    with open(result_json_file, 'r') as file:
        result_dict = json.load(file)

    return result_dict


@blueprint.route('/earth2sky')
def trade_history():
    template_var = {
        'request_args': {
            'data_type': request.args.get('data_type', data_type_list[0], type=str),
        },
        'data_type_list': data_type_list,
    }

    return render_template('earth2sky.html', **template_var)

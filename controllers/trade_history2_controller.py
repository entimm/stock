import os

import pandas as pd
from flask import Blueprint, render_template, request

from common.const import RESOURCES_PATH

blueprint = Blueprint('trade_history2', __name__)

file_list = [
    '水哥割股',
    '水哥割股2',
    '不颜不语',

]

@blueprint.route('/trade_history2_data')
def trade_history_data():

    name = request.args.get('name', file_list[0], type=str)
    csv_file = os.path.join(RESOURCES_PATH, '交割单', f'{name}.csv')
    df = pd.read_csv(csv_file, dtype={1: str})

    return df.to_dict(orient='records')


@blueprint.route('/trade_history2')
def trade_history():
    template_var = {
        'request_args': {
            'name': request.args.get('name', file_list[0], type=str)
        },
        'file_list': file_list,
        'socket_token': request.args.get('socket_token', '', str),
    }

    return render_template('trade_history2.html', **template_var)

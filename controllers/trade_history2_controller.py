import os

import pandas as pd
from flask import Blueprint, render_template, request

from common.common import RESOURCES_PATH

blueprint = Blueprint('trade_history2', __name__)


@blueprint.route('/trade_history2_data')
def trade_history_data():
    csv_file = os.path.join(RESOURCES_PATH, '水哥交割单.csv')
    df = pd.read_csv(csv_file, dtype={1: str})

    return df.to_dict(orient='records')


@blueprint.route('/trade_history2')
def trade_history():
    template_var = {
        'request_args': request.args.to_dict(),
        'socket_token': request.args.get('socket_token', '', str),
    }

    return render_template('trade_history2.html', **template_var)

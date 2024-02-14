import json
import os
from datetime import datetime

from flask import Blueprint, render_template, request

from common.const import RESOURCES_PATH

blueprint = Blueprint('market_height', __name__)


@blueprint.route('/market_height_data')
def market_height_data():
    json_file = os.path.join(RESOURCES_PATH, f'market_height.json')
    with open(json_file, 'r') as file:
        data_dict = json.load(file)

    year = request.args.get('year', datetime.now().year, type=int)
    if year == datetime.now().year:
        data_dict = {key: data_dict[key] for key in list(data_dict.keys())[-300:]}
    else:
        data_dict = {key: data_dict[key] for key in list(data_dict.keys()) if key[0:4] == str(year)}

    return data_dict


@blueprint.route('/market_height')
def market_height():
    year_list = list(range(datetime.now().year, 2018, -1))
    year = request.args.get('year', year_list[0], type=int)
    return render_template('market_height.html', **{
        'year_list': year_list,
        'request_args': {
            'year': year,
        }
    })

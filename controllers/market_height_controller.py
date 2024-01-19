import json
import os

from flask import Blueprint, render_template

from common.const import RESOURCES_PATH

blueprint = Blueprint('market_height', __name__)


@blueprint.route('/market_height_data')
def market_height_data():
    json_file = os.path.join(RESOURCES_PATH, f'market_height.json')
    with open(json_file, 'r') as file:
        data_dict = json.load(file)

    return data_dict


@blueprint.route('/market_height')
def market_height():
    return render_template('market_height.html', **{})

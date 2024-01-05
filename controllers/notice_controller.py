import json
import os

from flask import Blueprint, render_template

from app_cache import cache
from common.common import RESOURCES_PATH
from common.quotes import trade_date_list
from controllers import make_cache_key

blueprint = Blueprint('notice', __name__)

KAIPANLA_LIMITUP_PATH = os.path.join(RESOURCES_PATH, 'kaipanla/notice')


@blueprint.route('/notice_data')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def limited_power2_data():
    result_plate_list = {}
    for ts in trade_date_list.tail(200)['date'].to_list():
        date2 = ts.strftime('%Y-%m-%d')
        file_path = os.path.join(KAIPANLA_LIMITUP_PATH, f'notice_{date2}.json')
        if not os.path.exists(file_path): continue
        with open(file_path, 'r') as file:
            trades = json.load(file)

        result_plate_list[date2] = trades

    return result_plate_list


@blueprint.route('/notice')
def limited_power2():
    return render_template('notice.html', **{})

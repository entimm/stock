import os

import pandas as pd
from flask import Blueprint, render_template

from app_cache import cache
from common.const import RESOURCES_PATH
from common.config import config
from common.quotes import trade_date_list
from controllers import make_cache_key

blueprint = Blueprint('limited_power2', __name__)

KAIPANLA_LIMITUP_PATH = os.path.join(RESOURCES_PATH, 'kaipanla/limit_up')


@blueprint.route('/limited_power2_data')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def limited_power2_data():
    result_plate_list = {}
    for ts in trade_date_list.tail(500)['date'].to_list():
        date2 = ts.strftime('%Y-%m-%d')
        file_path = os.path.join(KAIPANLA_LIMITUP_PATH, f'{date2}.csv')
        if not os.path.exists(file_path): continue
        df = pd.read_csv(file_path, dtype={0: str})
        df['date'] = date2

        result_plate_list[date2] = df.to_dict(orient='records')

    return result_plate_list


@blueprint.route('/limited_power2')
def limited_power2():
    return render_template('limited_power2.html', **{})


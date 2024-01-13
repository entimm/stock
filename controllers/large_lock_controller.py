import os

import pandas as pd
from flask import Blueprint, render_template

from app_cache import cache
from common.const import RESOURCES_PATH
from common.quotes import trade_date_list
from controllers import make_cache_key

blueprint = Blueprint('large_lock', __name__)

KAIPANLA_LIMITUP_PATH = os.path.join(RESOURCES_PATH, 'kaipanla/limit_up')


@blueprint.route('/large_lock_data')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def large_lock_data():
    result_plate_list = {}
    for ts in trade_date_list.tail(500)['date'].to_list():
        date2 = ts.strftime('%Y-%m-%d')
        file_path = os.path.join(KAIPANLA_LIMITUP_PATH, f'{date2}.csv')
        if not os.path.exists(file_path): continue
        df = pd.read_csv(file_path, dtype={0: str})
        df = df[df['last_limit_ts'] == df['limit_ts']]
        df = df[df['const_num'] >= 1]

        df = df[pd.to_datetime(df['limit_ts'] + 3600 * 8, unit='s').dt.strftime('%H:%M') == '09:25']

        df = df[df['limit_amount'] >= 10 ** 8 * 1]

        result_plate_list[date2] = df.to_dict(orient='records')

    result_list = [
        {"date": date, **item}
        for date, values in result_plate_list.items()
        for item in values
    ]

    return list(reversed(result_list))


@blueprint.route('/large_lock')
def large_lock_limit():
    return render_template('large_lock.html', **{})

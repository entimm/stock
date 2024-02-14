import os
from datetime import datetime

import pandas as pd
from flask import Blueprint, render_template, request

from app_cache import cache
from common.const import RESOURCES_PATH
from common.quotes import trade_date_list
from controllers import make_cache_key

blueprint = Blueprint('limited_power2', __name__)

KAIPANLA_LIMITUP_PATH = os.path.join(RESOURCES_PATH, 'kaipanla/limit_up')


@blueprint.route('/limited_power2_data')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def limited_power2_data():
    year = request.args.get('year', datetime.now().year, type=int)
    df = trade_date_list
    if year == datetime.now().year:
        df = df.tail(300)
    else:
        df = df[df['date'].dt.year == year]

    result_plate_list = {}
    for ts in df['date'].to_list():
        date2 = ts.strftime('%Y-%m-%d')
        file_path = os.path.join(KAIPANLA_LIMITUP_PATH, f'{date2}.csv')
        if not os.path.exists(file_path): continue
        df = pd.read_csv(file_path, dtype={0: str})
        df['date'] = date2

        result_plate_list[date2] = df.fillna('').to_dict(orient='records')

    return result_plate_list


@blueprint.route('/limited_power2')
def limited_power2():
    year_list = list(range(datetime.now().year, 2018, -1))
    year = request.args.get('year', year_list[0], type=int)
    return render_template('limited_power2.html', **{
        'year_list': year_list,
        'request_args': {
            'year': year,
        }
    })

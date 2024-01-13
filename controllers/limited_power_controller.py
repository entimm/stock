import os

import pandas as pd
from flask import Blueprint, render_template

from app_cache import cache
from common.const import RESOURCES_PATH
from common.config import config
from common.quotes import trade_date_list
from controllers import make_cache_key

blueprint = Blueprint('limited_power', __name__)

XUANGUBAO_DETAIL_PATH = os.path.join(RESOURCES_PATH, 'xuangubao/details')


@blueprint.route('/limited_power_data')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def limited_power_data():
    result_plate_list = {}
    for ts in trade_date_list.tail(config.get('table_cols', 200))['date'].to_list():
        date = ts.strftime('%Y%m%d')
        date2 = ts.strftime('%Y-%m-%d')
        file_path = os.path.join(XUANGUBAO_DETAIL_PATH, f'detail-{date}.csv')
        if not os.path.exists(file_path): continue
        df = pd.read_csv(file_path)
        df = df[[
            'symbol',
            'stock_chi_name',
            'limit_up_days',
            'm_days_n_boards_days',
            'm_days_n_boards_boards',
            'first_limit_up',
            'last_limit_up',
            'buy_lock_volume_ratio',
            'non_restricted_capital',
            'turnover_ratio',
            'break_limit_up_times',
            'listed_date',
            'reason_desc',
            'related_plates',
        ]]
        df.fillna('', inplace=True)
        result_plate_list[date2] = df.to_dict(orient='records')

    return result_plate_list


@blueprint.route('/limited_power')
def limited_power():
    return render_template('limited_power.html', **{})

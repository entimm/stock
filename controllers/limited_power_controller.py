import json
import os

import pandas as pd
from flask import Blueprint, render_template

from app_cache import cache
from common.common import RESOURCES_PATH
from common.config import config
from common.quotes import trade_date_list
from common.xuangubao import row2info
from controllers import make_cache_key

blueprint = Blueprint('limited_power', __name__)

XUANGUBAO_DETAIL_PATH = os.path.join(RESOURCES_PATH, 'xuangubao', 'details')


@blueprint.route('/limited_power')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def limited():
    result_plate_list = {}
    result_stock_list = {}
    for ts in trade_date_list.tail(config.get('table_cols', 200))['date'].to_list():
        plate_dict = {}
        stock_list = []
        date = ts.strftime('%Y%m%d')
        date2 = ts.strftime('%Y-%m-%d')
        file_path = os.path.join(XUANGUBAO_DETAIL_PATH, f'detail-{date}.csv')
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            related_plates = []
            if not isinstance(row['surge_reason.related_plates'], float):
                related_plates = json.loads(row['surge_reason.related_plates'].replace("'", '"'))
            for item in related_plates:
                plate_dict.setdefault(item['plate_name'], {'plate_reason': item.get('plate_reason', '空'), 'stock_list': []})['stock_list'].append(row['symbol'])

            stock_data = row2info(row.to_dict())
            stock_data['date'] = date2
            stock_data['plate_names'] = [item['plate_name'] for item in related_plates]

            stock_list.append(stock_data)

        result_plate_list[date2] = [{'plate_name': name, 'plate_reason': item['plate_reason'], 'stock_list': item['stock_list']} for name, item in plate_dict.items()]
        result_stock_list[date2] = sorted(stock_list, key=lambda x: -x['m_days_n_boards_boards'])

    template_var = {
        'result_plate_list': dict(reversed(result_plate_list.items())),
        'result_stock_list': dict(reversed(result_stock_list.items())),
    }

    return render_template('limited_power.html', **template_var)

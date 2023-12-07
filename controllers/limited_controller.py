import os

import pandas as pd
from flask import Blueprint, render_template, request

from app_cache import cache
from common.common import TOTAL_PATH
from common.config import config
from common.data import ticker_name_dict
from common.quotes import trade_date_list
from controllers import make_cache_key

blueprint = Blueprint('limit_stock', __name__)


@blueprint.route('/limited')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def limited():
    direction_list = {
        1: {'name': '涨停'},
        2: {'name': '跌停'},
        3: {'name': '大肉'},
        4: {'name': '大面'},
    }
    direction = request.args.get('direction', 1, type=int)

    result_dict = {}
    for date in trade_date_list.tail(config.get('table_cols', 200))['date'].to_list():
        date = date.strftime('%Y%m%d')
        csv_file = os.path.join(TOTAL_PATH, f'data_{date}.csv')
        if not os.path.exists(csv_file): continue
        df = pd.read_csv(csv_file)
        df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
        match direction:
            case 1:
                df = df[df['high'] == df['close']]
                df = df[df['pct_chg'] >= 9.6]
                df = df.sort_values(by='pct_chg', ascending=False)
                df['max_result'] = (df['close'] / df['low'] - 1) * 100
            case 2:
                df = df[df['low'] == df['close']]
                df = df[df['pct_chg'] <= -9.6]
                df = df.sort_values(by='pct_chg', ascending=True)
                df['max_result'] = (df['close'] / df['high'] - 1) * 100
            case 3:
                df['max_result'] = (df['close'] / df['low'] - 1) * 100
                df = df[df['max_result'] >= 9.6]
                df = df.sort_values(by='max_result', ascending=False)
            case _:
                df['max_result'] = (df['close'] / df['high'] - 1) * 100
                df = df[df['max_result'] <= -9.6]
                df = df.sort_values(by='max_result', ascending=True)

        df['pct_chg'] = round(df['pct_chg'], 2)
        df['max_result'] = round(df['max_result'], 2)

        df['ts_code'] = df['ts_code'].str[:6]
        df['ts_name'] = df['ts_code'].map(ticker_name_dict)
        df['show'] = df['ts_name'].astype(str) + '|' + df['ts_code'].astype(str) + '|' + df['pct_chg'].astype(str) + '|' + df['max_result'].astype(str)

        result_dict[f"{date[:4]}-{date[4:6]}-{date[6:]}"] = df['show'].to_list()

    template_var = {
        'data': dict(reversed(result_dict.items())),
        'direction_list': direction_list,
        'request_args': {
            'direction': direction,
        }
    }

    return render_template('limited.html', **template_var)

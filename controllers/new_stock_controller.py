import os

import pandas as pd
from flask import Blueprint, render_template, request

from app_cache import cache
from common.const import RESOURCES_PATH
from controllers import make_cache_key

blueprint = Blueprint('new_stock', __name__)


@blueprint.route('/new_stock')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def new_stock():
    df = pd.read_csv(os.path.join(RESOURCES_PATH, 'a_stock_meta_list.csv'), dtype={0: str, 1: str})
    df = df.sort_values(by='list_date', ascending=False).head(200)
    df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
    df = df[['symbol', 'name', 'list_date']]
    df['list_date'] = pd.to_datetime(df['list_date'], format='%Y%m%d')

    df['list_week'] = df['list_date'].dt.to_period('W').astype(str)

    df['show'] = df['name'].astype(str) + '|' + df['symbol'].astype(str) + '|0'

    result_dict = df.groupby('list_week').apply(lambda group: group['show'].to_list())

    template_var = {
        'data': dict(reversed(list(result_dict.items()))),
        'request_args': {
            'socket_token': request.args.get('socket_token', '', str),
        }
    }
    #
    return render_template('new_stock.html', **template_var)

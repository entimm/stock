import os

import pandas as pd
from flask import Blueprint, render_template, request

from app_cache import cache
from common.const import RESOURCES_PATH, TOTAL_PATH
from common.quotes import trade_date_list
from controllers import make_cache_key

blueprint = Blueprint('new_stock', __name__)


@blueprint.route('/new_stock')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def new_stock():
    df = pd.read_csv(os.path.join(RESOURCES_PATH, 'a_stock_meta_list.csv'), dtype={0: str, 1: str})
    df = df.sort_values(by='list_date', ascending=False).head(1000)
    df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
    df = df[['symbol', 'name', 'list_date', 'ts_code']]

    df['list_date'] = pd.to_datetime(df['list_date'], format='%Y%m%d')
    df['list_week'] = df['list_date'].dt.to_period('M').astype(str)

    latest_date = trade_date_list.loc[trade_date_list.index[-1], 'date']
    csv_file = os.path.join(TOTAL_PATH, f'data_{latest_date.strftime("%Y%m%d")}.csv')
    quotes_df = pd.read_csv(csv_file)
    df_merged = pd.merge(df, quotes_df, on='ts_code')

    df_merged['show'] = df_merged['name'].astype(str) + '|' + df_merged['symbol'].astype(str) + '|' + df_merged['pct_chg'].astype(str)

    result_dict = df_merged.groupby('list_week').apply(lambda group: group['show'].to_list()).tail(24)

    template_var = {
        'data': dict(reversed(list(result_dict.items()))),
        'request_args': {
            'socket_token': request.args.get('socket_token', '', str),
        }
    }
    #
    return render_template('new_stock.html', **template_var)

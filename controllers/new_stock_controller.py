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
    latest_date = trade_date_list.loc[trade_date_list.index[-1], 'date']
    date_str = request.args.get('date', latest_date.strftime("%Y-%m-%d"), str)
    date_int = date_str.replace('-', '')

    df = pd.read_csv(os.path.join(RESOURCES_PATH, 'a_stock_meta_list.csv'), dtype={0: str, 1: str})
    df = df[df['list_date'] <= int(date_int)]
    df = df.sort_values(by='list_date', ascending=False).head(1000)
    df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
    df = df[['symbol', 'name', 'list_date', 'ts_code']]

    df['list_date'] = pd.to_datetime(df['list_date'], format='%Y%m%d')
    df['list_week'] = df['list_date'].dt.to_period('M').astype(str)

    csv_file = os.path.join(TOTAL_PATH, f'data_{date_int}.csv')
    if os.path.exists(csv_file):
        quotes_df = pd.read_csv(csv_file)
        df = pd.merge(df, quotes_df, on='ts_code')

    df['pct_chg'] = df['pct_chg'] if 'pct_chg' in df.columns else 0
    df['close'] = df['close'] if 'close' in df.columns else 0
    df['show'] = df['name'].astype(str) + '|' + df['symbol'].astype(str) + '|' + df['pct_chg'].astype(str) + '|' + df['close'].astype(str)

    result_dict = df.groupby('list_week').apply(lambda group: group['show'].to_list()).tail(24)

    template_var = {
        'data': dict(reversed(list(result_dict.items()))),
        'request_args': {
            'socket_token': request.args.get('socket_token', '', str),
        }
    }
    #
    return render_template('new_stock.html', **template_var)

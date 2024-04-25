import os

import pandas as pd
from flask import Blueprint, render_template, request

from app_cache import cache
from common.const import RESOURCES_PATH
from common.quotes import trade_date_list
from controllers import make_cache_key

blueprint = Blueprint('bid', __name__)

KAIPANLA_LIMITUP_PATH = os.path.join(RESOURCES_PATH, 'kaipanla/bid')


@blueprint.route('/bid_data')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def bid_data():
    default_date = trade_date_list['date'].to_list()[-1].strftime('%Y-%m-%d')
    date = request.args.get('date', default_date, type=str)

    file_path = os.path.join(KAIPANLA_LIMITUP_PATH, f'{date}.csv')
    if not os.path.exists(file_path):
        return []

    df = pd.read_csv(file_path, dtype={0: str})

    return df.fillna('').to_dict(orient='records')


@blueprint.route('/bid')
def bid():
    default_date = trade_date_list['date'].to_list()[-1].strftime('%Y-%m-%d')
    date = request.args.get('date', default_date, type=str)
    return render_template('bid.html', **{
        'date_list': nearbyDate(date),
        'request_args': {
            'date': date,
        }
    })


def nearbyDate(date):
    trade_date_list['date'] = pd.to_datetime(trade_date_list['date'])
    date_index = trade_date_list.index[trade_date_list['date'] == pd.to_datetime(date)].tolist()
    num = 15

    if date_index:
        specific_index = date_index[0]

        start_index = max(0, specific_index - num)
        end_index = min(len(trade_date_list) - 1, specific_index + num)

        filtered_df = trade_date_list.iloc[start_index:end_index + 1]
    else:
        filtered_df = trade_date_list.iloc[-num * 2:]

    return [item.strftime('%Y-%m-%d') for item in filtered_df['date'].to_list()]

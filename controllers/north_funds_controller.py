import pandas as pd
from flask import Blueprint, render_template, request
from pandas import Series

from common.common import NORTH_FUNDS_FILE_PATH

blueprint = Blueprint('north_funds', __name__)


@blueprint.route('/north_funds')
def ipo():
    df = pd.read_csv(NORTH_FUNDS_FILE_PATH, dtype={0: str})
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')

    field_list = [
        "ggt_ss", "ggt_sz", "hgt", "sgt", "north_money", "south_money"
    ]
    field = request.args.get('field', 'north_money')

    df['trade_week'] = df['trade_date'].dt.to_period('W').astype(str)
    df['trade_month'] = df['trade_date'].dt.to_period('M').astype(str)
    df['trade_year'] = df['trade_date'].dt.to_period('Y').astype(str)

    df['trade_date'] = df['trade_date'].astype(str)

    daily_count: Series = df.groupby('trade_date')[field].sum()
    weekly_count: Series = df.groupby('trade_week')[field].sum()
    monthly_count: Series = df.groupby('trade_month')[field].sum()
    yearly_count: Series = df.groupby('trade_year')[field].sum()

    template_var = {
        'daily_count': daily_count.to_dict(),
        'weekly_count': weekly_count.to_dict(),
        'monthly_count': monthly_count.to_dict(),
        'yearly_count': yearly_count.to_dict(),
        'field_list': field_list,
        'request_args': {
            'field': field,
        }
    }

    return render_template('north_funds.html', **template_var)

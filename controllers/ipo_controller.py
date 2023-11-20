from datetime import datetime

import pandas as pd
from flask import Blueprint, render_template
from pandas import Series

from common.data import stock_meta_df

blueprint = Blueprint('ipo', __name__)


@blueprint.route('/ipo')
def ipo():
    stock_meta_df['list_date'] = pd.to_datetime(stock_meta_df['list_date'], format='%Y%m%d')

    stock_meta_df['list_week'] = stock_meta_df['list_date'].dt.to_period('W').astype(str)
    stock_meta_df['list_month'] = stock_meta_df['list_date'].dt.to_period('M').astype(str)
    stock_meta_df['list_year'] = stock_meta_df['list_date'].dt.to_period('Y').astype(str)

    weekly_count: Series = stock_meta_df.groupby('list_week').size()
    monthly_count: Series = stock_meta_df.groupby('list_month').size()
    yearly_count: Series = stock_meta_df.groupby('list_year').size()


    template_var = {
        'weekly_count': weekly_count.to_dict(),
        'monthly_count': monthly_count.to_dict(),
        'yearly_count': yearly_count.to_dict(),
    }

    return render_template('ipo.html', **template_var)

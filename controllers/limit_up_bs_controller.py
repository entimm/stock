import os

import pandas as pd
from flask import Blueprint, render_template, request

from common.const import RESOURCES_PATH
from common.utils import ticker_name

blueprint = Blueprint('limit_up_bs', __name__)


@blueprint.route('/limit_up_bs_data')
def limit_up_bs_data():
    csv_file = os.path.join(RESOURCES_PATH, 'limit_up_bs.csv')
    df = pd.read_csv(csv_file, dtype={0: str})
    df = df.sort_values(by='buy_date', ascending=True)
    df['name'] = df['symbol'].apply(ticker_name)

    return df.tail(2000).to_dict(orient='records')


@blueprint.route('/limit_up_bs')
def limit_up_bs():
    template_var = {
        'request_args': request.args.to_dict(),
    }

    return render_template('limit_up_bs.html', **template_var)

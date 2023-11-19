import os

import pandas as pd
from flask import Blueprint, render_template, request
from mootdx.reader import Reader

from common.common import TDX_DIR, TOTAL_PATH
from common.data import symbol_name_dict

blueprint = Blueprint('limit_stock', __name__)


@blueprint.route('/limited')
def limited():
    reader = Reader.factory(market='std', tdxdir=TDX_DIR)
    date_list = reader.daily(symbol='999999').reset_index().tail(100)['date'].to_list()

    direction_list = {
        1: {'name': '涨'},
        2: {'name': '跌'},
    }
    direction = request.args.get('direction', 1, type=int)

    result_dict = {}
    for date in date_list:
        date = date.strftime('%Y%m%d')
        csv_file = os.path.join(TOTAL_PATH, f'data_{date}.csv')
        df = pd.read_csv(csv_file)
        df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
        if direction == 1:
            df = df[df['high'] == df['close']]
            condition = df['pct_chg'] >= 9.6
        else:
            df = df[df['low'] == df['close']]
            condition = df['pct_chg'] <= -9.6
        df = df[condition]
        df['pct_chg'] = round(df['pct_chg'], 2)

        df['ts_code'] = df['ts_code'].str[:6]
        df['ts_name'] = df['ts_code'].map(symbol_name_dict)
        df['show'] = df['ts_name'].astype(str) + '|' + df['ts_code'].astype(str) + '|' + df['pct_chg'].astype(str)

        result_dict[f'-{date}-'] = df['show'].to_list()

    print(result_dict)

    template_var = {
        'data': dict(reversed(result_dict.items())),
        'direction_list': direction_list,
        'direction': direction,
    }

    return render_template('limited.html', **template_var)

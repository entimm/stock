import os

import pandas as pd
from flask import Blueprint, render_template, request

from common.common import TOTAL_PATH
from common.data import symbol_name_dict, trade_date_list

blueprint = Blueprint('limit_stock', __name__)


@blueprint.route('/limited')
def limited():
    direction_list = {
        1: {'name': '涨停'},
        2: {'name': '跌停'},
        3: {'name': '大喜'},
        4: {'name': '大面'},
    }
    direction = request.args.get('direction', 1, type=int)

    result_dict = {}
    for date in trade_date_list:
        date = date.strftime('%Y%m%d')
        csv_file = os.path.join(TOTAL_PATH, f'data_{date}.csv')
        df = pd.read_csv(csv_file)
        df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
        if direction == 1:
            df = df[df['high'] == df['close']]
            df = df[df['pct_chg'] >= 9.6]
            df = df.sort_values(by='pct_chg', ascending=False)
            df['max_result'] = (df['close'] / df['low'] - 1) * 100
        elif direction == 2:
            df = df[df['low'] == df['close']]
            df = df[df['pct_chg'] <= -9.6]
            df = df.sort_values(by='pct_chg', ascending=True)
            df['max_result'] = (df['close'] / df['high'] - 1) * 100
        elif direction == 3:
            df['max_result'] = (df['close'] / df['low'] - 1) * 100
            df = df[df['max_result'] >= 9.6]
            df = df.sort_values(by='max_result', ascending=False)
        else:
            df['max_result'] = (df['close'] / df['high'] - 1) * 100
            df = df[df['max_result'] <= -9.6]
            df = df.sort_values(by='max_result', ascending=True)

        df['pct_chg'] = round(df['pct_chg'], 2)
        df['max_result'] = round(df['max_result'], 2)

        df['ts_code'] = df['ts_code'].str[:6]
        df['ts_name'] = df['ts_code'].map(symbol_name_dict)
        df['show'] = df['ts_name'].astype(str) + '|' + df['ts_code'].astype(str) + '|' + df['pct_chg'].astype(str) + '|' + df['max_result'].astype(str)

        result_dict[f'-{date}-'] = df['show'].to_list()

    template_var = {
        'data': dict(reversed(result_dict.items())),
        'direction_list': direction_list,
        'direction': direction,
    }

    return render_template('limited.html', **template_var)

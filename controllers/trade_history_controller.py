import os

import pandas as pd
from flask import Blueprint, render_template, request

from common.const import RESOURCES_PATH

blueprint = Blueprint('trade_history', __name__)


@blueprint.route('/trade_history_data')
def trade_history_data():
    csv_file = os.path.join(RESOURCES_PATH, 'trade_history.csv')
    df = pd.read_csv(csv_file, dtype={1: str})

    df = df.groupby(['成交日期', '证券代码', '操作']).agg({
        '成交日期': 'first',
        '证券代码': 'first',
        '证券名称': 'first',
        '操作': 'first',
        '成交数量': 'sum',
        '成交价格': 'mean',
    })

    df['profit_amount'] = 0
    df['profit_pct'] = 0

    holding = {}
    for index, row in df.iterrows():
        if row['操作'] == '买':
            holding.setdefault(row['证券代码'], {'num': 0, 'buy_amount': 0, 'sell_amount': 0})
            holding[row['证券代码']]['num'] += row['成交数量']
            holding[row['证券代码']]['buy_amount'] += row['成交数量'] * row['成交价格']

        if row['操作'] == '卖':
            holding[row['证券代码']]['num'] -= row['成交数量']
            holding[row['证券代码']]['sell_amount'] += row['成交数量'] * row['成交价格']

        if holding[row['证券代码']]['num'] == 0:
            df.at[index, 'profit_amount'] = row['profit_amount'] = holding[row['证券代码']]['sell_amount'] - holding[row['证券代码']]['buy_amount']
            holding.pop(row['证券代码'], None)

    if sort := request.args.get('sort', type=str):
        asc = sort == 'asc'
        df = df.sort_values(by='profit_amount', ascending=asc)

    return df.to_dict(orient='records')


@blueprint.route('/trade_history')
def trade_history():
    template_var = {
        'request_args': request.args.to_dict(),
    }

    return render_template('trade_history.html', **template_var)

import json
import os

from flask import Blueprint, render_template, request

from common.const import RESOURCES_PATH, PeriodEnum
from common.quotes import fetch_local_plus_real
from common.utils import ticker_name, row_to_kline

blueprint = Blueprint('backtest', __name__)


@blueprint.route('/backtest_result_data')
def backtest_result_data():
    symbol = request.args.get('symbol', '', type=str)
    result_json_file = os.path.join(RESOURCES_PATH, 'backtest', f'back_test_{symbol}.json' if symbol else 'back_test.json')
    with open(result_json_file, 'r') as file:
        trades = json.load(file)

    result_list = generate_order(trades)

    return result_list


@blueprint.route('/backtest_result')
def backtest_result():
    symbol = request.args.get('symbol', '', type=str)
    period = request.args.get('period', 'D', type=str)
    ma = request.args.get('ma', '5,10,20,60', type=str).split(',')
    result_json_file = os.path.join(RESOURCES_PATH, 'backtest', f'back_test_{symbol}.json' if symbol else 'back_test.json')
    kline_list = []
    if symbol:
        df = fetch_local_plus_real(symbol, PeriodEnum[period])
        kline_list = df.apply(row_to_kline, axis=1).to_list()
    if not os.path.exists(result_json_file):
        return '没有数据'
    with open(result_json_file, 'r') as file:
        trades = json.load(file)

    get_color_func = get_color()

    template_var = {
        'kline_list': kline_list,
        'backtest_trades': trades,
        'indicator_config': {
            'ma': [{'period': item, 'color': get_color_func(), 'size': 1} for item in ma]
        },
        'request_args': request.args.to_dict(),
    }

    return render_template('backtest_result.html', **template_var)


def generate_order(trades, initial_capital=1000000):
    order = {}
    capital = initial_capital
    buy_date = ''
    buy_price = 0
    hold_vol = 0

    for trade in trades:
        if trade["action"] == "BUY":
            buy_date = trade["date"]
            buy_price = trade["price"]

            hold_vol = (capital // trade["price"]) // 100 * 100
            hold_amount = hold_vol * trade["price"]

            capital -= hold_amount
        elif trade["action"] == "SELL":
            capital += hold_vol * trade["price"]
            profit = round((trade["price"] / buy_price - 1) * 100, 2)

            hold_vol = 0
            hold_amount = 0

            order[trade["date"]] = {
                'capital': round(capital + hold_amount, 2),
                'symbol': trade.get('symbol', ''),
                'name': ticker_name(trade.get('symbol', '')),
                'profit': profit,
                'price': round(trade["price"], 2),
                'date_desc': f'{buy_date} - {trade["date"]}'
            }

    if trades[-1]['action'] == 'BUY':
        last_trade = trades[-1]
        order[last_trade["date"]] = {
            'capital': round(capital + buy_price * hold_vol, 2),
            'symbol': last_trade.get('symbol', ''),
            'name': ticker_name(last_trade.get('symbol', '')),
            'profit': 0,
            'price': round(buy_price, 2),
            'date_desc': f'{buy_date} - '
        }

    return order


def get_color():
    i = 0
    color = [
        '#930606',
        '#ECAB07',
        '#EF15DE',
        '#16DE45',
        '#6E28E5',
        '#E50B33',
        '#16B9DE',
    ]

    def _get_color():
        nonlocal i, color
        i += 1
        return color[i % len(color)]

    return _get_color

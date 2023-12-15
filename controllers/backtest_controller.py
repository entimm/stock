import json
import os

from flask import Blueprint, render_template, request

from common.cmd_utils import get_hfq_kline
from common.common import RESOURCES_PATH
from common.utils import ticker_name, row_to_kline

blueprint = Blueprint('backtest', __name__)


@blueprint.route('/backtest_result_data')
def backtest_result_data():
    symbol = request.args.get('symbol', '', type=str)
    result_json_file = os.path.join(RESOURCES_PATH, f'back_test_{symbol}.json' if symbol else 'back_test.json')
    with open(result_json_file, 'r') as file:
        trades = json.load(file)
    result_list = generate_order(trades)

    return result_list


@blueprint.route('/backtest_result')
def backtest_result():
    return render_template('backtest_result.html', **{
        'symbol': request.args.get('symbol', '', type=str)
    })


@blueprint.route('/backtest_kline_ma')
def backtest_kline_ma():
    symbol = request.args.get('symbol', '', type=str)
    result_json_file = os.path.join(RESOURCES_PATH, f'back_test_{symbol}.json' if symbol else 'back_test.json')
    if not symbol or not os.path.exists(result_json_file):
        return '没有数据'
    with open(result_json_file, 'r') as file:
        trades = json.load(file)
    df = get_hfq_kline(symbol)
    kline_list = df.apply(row_to_kline, axis=1).to_list()

    template_var = {
        'kline_list': kline_list,
        'backtest_trades': trades,
        'indicator_config': {
            'ma': [
                {'period': 15, 'color': '#930606', 'size': 1},
                {'period': 60, 'color': '#ECAB07', 'size': 1},
                {'period': 432, 'color': '#EF15DE', 'size': 1},
            ]
        },
        'request_args': request.args.to_dict(),
    }

    return render_template('backtest_kline.html', **template_var)


def generate_order(trades, initial_capital=100000):
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
            change_rate = round((trade["price"] / buy_price - 1) * 100, 2)

            hold_vol = 0
            hold_amount = 0

            order[trade["date"]] = {
                'capital': round(capital + hold_amount, 2),
                'symbol': trade.get('symbol', ''),
                'name': ticker_name(trade.get('symbol', '')),
                'change_rate': change_rate,
                'price': round(trade["price"], 2),
                'date_desc': f'{buy_date} - {trade["date"]}'
            }

    return order

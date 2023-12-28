import json
import os

from flask import Blueprint, render_template, request

from common.cmd_utils import get_forex_kline
from common.common import RESOURCES_PATH, PeriodEnum
from common.quotes import fetch_local_plus_real
from common.utils import ticker_name, row_to_kline

blueprint = Blueprint('backtest', __name__)

forex_symbols = ['XAUUSD']

@blueprint.route('/backtest_result_data')
def backtest_result_data():
    symbol = request.args.get('symbol', '', type=str)
    result_json_file = os.path.join(RESOURCES_PATH, 'backtest', f'back_test_{symbol}.json' if symbol else 'back_test.json')
    with open(result_json_file, 'r') as file:
        trades = json.load(file)

    if symbol in forex_symbols:
        result_list = generate_order_leverage(trades)
    else:
        result_list = generate_order(trades)

    return result_list


@blueprint.route('/backtest_result')
def backtest_result():
    symbol = request.args.get('symbol', '', type=str)
    period = request.args.get('period', 'D', type=str)
    result_json_file = os.path.join(RESOURCES_PATH, 'backtest', f'back_test_{symbol}.json' if symbol else 'back_test.json')
    kline_list = []
    if symbol:
        if symbol in forex_symbols:
            df = get_forex_kline(symbol, PeriodEnum[period])
        else:
            df = fetch_local_plus_real(symbol, PeriodEnum[period])
        kline_list = df.apply(row_to_kline, axis=1).to_list()
    if not os.path.exists(result_json_file):
        return '没有数据'
    with open(result_json_file, 'r') as file:
        trades = json.load(file)

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

    return render_template('backtest_result.html', **template_var)


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


def generate_order_leverage(trades, initial_capital=100000):
    leverage = 150
    bet_percentage = 0.01

    order = {}
    capital = initial_capital
    buy_date = ''
    buy_price = 0
    hold_vol = 0

    for trade in trades:
        if trade["action"] == "BUY":
            buy_date = trade["date"]
            buy_price = trade["price"]

            hold_vol = (capital * bet_percentage * leverage // trade["price"])
        elif trade["action"] == "SELL":
            profit = round((trade["price"] - buy_price) * hold_vol, 2)
            capital = capital + profit

            hold_vol = 0

            order[trade["date"]] = {
                'capital': round(capital, 2),
                'symbol': trade.get('symbol', ''),
                'name': ticker_name(trade.get('symbol', '')),
                'profit': profit,
                'price': round(trade["price"], 2),
                'date_desc': f'{buy_date} - {trade["date"]}'
            }
            print(order[trade["date"]])

    return order

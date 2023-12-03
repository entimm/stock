from datetime import datetime, timedelta

from flask import Blueprint, request, render_template

from common.common import PeriodEnum
from common.quotes import fetch_local_plus_real
from common.utils import ticker_name

blueprint = Blueprint('line2', __name__)


@blueprint.route('/line2')
def line2():
    date = request.args.get('date')
    flag = int(request.args.get('flag', 0))

    if date:
        start = f'{date} 00:00:00' if flag != 0 else None
        end = f'{date} 23:59:59' if flag == 0 else None
    else:
        start = request.args.get('start', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')) + ' 00:00:00'
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d')) + ' 23:59:59'

    symbols = [x for x in request.args.get('symbols', '').split('-') if x]
    period = request.args.get('period', 'D', type=str).upper()
    length = request.args.get('length', 400, type=int)
    num = request.args.get('num', 5, type=int)

    period_enum = PeriodEnum[period]
    chart_data = []

    index_symbols = ['999999', '399006']
    symbols += index_symbols

    for symbol in symbols:
        df = fetch_local_plus_real(symbol, period_enum, 1)[start:end]
        df = df.tail(length) if flag == 0 else df.head(length)
        df.index = df.index.strftime("%Y-%m-%d %H:%M:%S")
        df['value'] = round((df['close'] / df['close'].iloc[0] - 1) * 100, 2)

        item_data = {
            'symbol': symbol,
            'name': ticker_name(symbol),
            'values': df['value'].to_dict(),
            'broad_index': 1 if symbol in index_symbols else 0,
        }

        chart_data.append(item_data)

    template_var = {
        'chart_data': chart_data,
        'request_args': {
            'date': date,
            'period': period,
            'flag': flag,
            'num': num,
            'symbols': request.args.get('symbols', ''),
        },
        'period_list': {
            PeriodEnum.F1.name: '1分钟',
            PeriodEnum.F5.name: '5分钟',
            PeriodEnum.F15.name: '15分钟',
            PeriodEnum.F30.name: '30分钟',
            PeriodEnum.D.name: '天',
        },
        'flag_list': [
            '前',
            '后',
        ],
        'num_list': [
            5,
            10,
            20,
        ],
    }

    return render_template('line2.html', **template_var)

import json
import math
import os
import re
from datetime import datetime
from urllib.parse import urlencode

import requests

from common.data import gnbk_dict, etf_dict, ticker_name_dict, index_dict


def filter_files_by_date(directory, file_pattern):
    file_regex = re.compile(file_pattern)

    file_list = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if match := file_regex.match(file):
                file_list.append((os.path.join(root, file), match.group(1)))

    return file_list


def minutes_since_open():
    now = datetime.now()
    if now.weekday() in [5, 6]:
        return 0

    open_time = datetime(now.year, now.month, now.day, 9, 30)
    close_time = datetime(now.year, now.month, now.day, 16, 00)
    if open_time < now < close_time:
        diff = min(now, close_time) - open_time
        return math.ceil(diff.total_seconds() / 60)

    return 0


def symbol_type(symbol):
    if symbol[0:2] == '88':
        return 'GNBK'
    elif symbol[0:2] in ['15', '51', '56', '58']:
        return 'ETF'
    elif symbol in ['999999'] or symbol[0:3] == '399':
        return 'INDEX'
    else:
        return 'STOCK'


def ticker_name(symbol):
    match symbol_type(symbol):
        case 'GNBK':
            return gnbk_dict.get(symbol, symbol).replace('概念', '')
        case 'ETF':
            return etf_dict.get(symbol, symbol)
        case 'INDEX':
            return index_dict.get(symbol, symbol)
        case _:
            return ticker_name_dict[symbol]


def symbol_all():
    symbol_dict = ticker_name_dict | index_dict | gnbk_dict | etf_dict
    return [{'key': k, 'value': v} for k, v in symbol_dict.items()]


def row_to_kline(row):
    return {
        'time': row.name.strftime("%Y-%m-%d %H:%M:%S"),
        'open': row['open'],
        'high': row['high'],
        'low': row['low'],
        'close': row['close'],
        'volume': row['volume'],
        'pct_change': row['pct_change'] if not math.isnan(row['pct_change']) else '',
    }


def create_href(params):
    params = {key: int(value) if isinstance(value, bool) else value for key, value in params.items()}

    return f'?{urlencode(params)}'


def create_link(request_args, update_args, highlight_condition, text):
    request_args = request_args | update_args
    highlight_attr = 'class ="highlight"' if highlight_condition else ''

    return f'<a href="{create_href(request_args)}" {highlight_attr}>{text}</a>'


def send_request(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    return json.loads(response.text)
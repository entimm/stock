import math
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
from mootdx.quotes import Quotes

from common.common import PeriodEnum, TDX_FREQUENCY_MAP, TDX_BLOCK_NEW_PATH
from common.data import local_tdx_reader, gnbk_dict, etf_dict, ticker_name_dict, index_dict
from common.price_calculate import resample_kline


def read_tdx_text(file_path):
    df = pd.read_csv(file_path, header=1, skipfooter=1, engine='python', encoding='gbk', sep='\t', index_col=None,
                     dtype={0: str}, skipinitialspace=True)

    df.columns = df.columns.str.strip()
    df = df.iloc[:, :-1]
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)

    return df


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


def fetch_local_data(reader, symbol, period):
    match period:
        case PeriodEnum.F1:
            return reader.minute(symbol=symbol)
        case PeriodEnum.F5:
            return reader.fzline(symbol=symbol)
        case PeriodEnum.D:
            return reader.daily(symbol=symbol)


def realtime_whole_df(symbol, period_enum, req_real=1):
    base_period_enum = PeriodEnum.F1 if period_enum in [PeriodEnum.F15, PeriodEnum.F30] else period_enum

    frequency = TDX_FREQUENCY_MAP.get(base_period_enum)
    df = fetch_local_data(local_tdx_reader, symbol, base_period_enum)
    if req_real:
        if minutes := minutes_since_open():
            match base_period_enum:
                case PeriodEnum.D:
                    offset = 5
                case PeriodEnum.F1:
                    offset = minutes
                case _:
                    offset = minutes / 5

            tp = symbol_type(symbol)
            if tp in ['INDEX', 'GNBK']:
                client = Quotes.factory(market='std')
                real_time_df = client.index(symbol=symbol, frequency=frequency, offset=offset)
            else:
                client = Quotes.factory(market='std')
                real_time_df = client.bars(symbol=symbol, frequency=frequency, offset=offset)
            if period_enum == PeriodEnum.D:
                real_time_df = real_time_df[real_time_df.index.date > df.index[-1].date()]
            else:
                real_time_df = real_time_df[real_time_df.index > df.index[-1]]
            df = pd.concat([df, real_time_df[['open', 'high', 'low', 'close', 'amount', 'volume']]], axis=0)

    if period_enum in [PeriodEnum.F15, PeriodEnum.F30]:
        df = resample_kline(df, period_enum)

    return df


def read_bk(bk_key):
    zxg_file = os.path.join(TDX_BLOCK_NEW_PATH, f'{bk_key}.blk')

    if not Path(zxg_file).exists():
        raise Exception("file not exists")

    codes = open(zxg_file).read().splitlines()

    return [c[1:] for c in codes if c != ""]


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
    symbol_dict = {**ticker_name_dict, **index_dict, **gnbk_dict, **etf_dict}
    return [{'key': k, 'value': v} for k, v in symbol_dict.items()]


def row_to_kline(row):
    return {
        'time': row.name.strftime("%Y-%m-%d %H:%M:%S"),
        'open': row['open'],
        'high': row['high'],
        'low': row['low'],
        'close': row['close'],
        'volume': row['volume'],
    }


def create_href(params):
    params = {key: int(value) if isinstance(value, bool) else value for key, value in params.items()}

    return f'?{urlencode(params)}'


def create_link(request_args, update_args, highlight_condition, text):
    request_args = {**request_args, **update_args}
    highlight_attr = 'class ="highlight"' if highlight_condition else ''

    return f'<a href="{create_href(request_args)}" {highlight_attr}>{text}</a>'

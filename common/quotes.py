import os.path
from datetime import datetime

import pandas as pd
from mootdx.quotes import Quotes
from mootdx.reader import Reader

from common.const import TDX_FREQUENCY_MAP, PeriodEnum, TDX_PATH
from common.config import config
from common.price_calculate import resample_kline
from common.utils import symbol_type, minutes_since_open

client = Quotes.factory(market='std')
local_tdx_reader = Reader.factory(market='std', tdxdir=TDX_PATH)


def fetch_real(symbol, period_enum, offset):
    frequency = TDX_FREQUENCY_MAP.get(period_enum)
    if symbol_type(symbol) in ['INDEX', 'GNBK']:
        real_time_df = client.index(symbol=symbol, frequency=frequency, offset=offset)
    else:
        real_time_df = client.bars(symbol=symbol, frequency=frequency, offset=offset)

    return real_time_df


def fetch_latest_daily(symbols):
    return client.quotes(symbol=symbols)


def fetch_local_data(symbol, period):
    match period:
        case PeriodEnum.F1:
            return local_tdx_reader.minute(symbol=symbol)
        case PeriodEnum.F5:
            return local_tdx_reader.fzline(symbol=symbol)
        case PeriodEnum.D:
            return local_tdx_reader.daily(symbol=symbol)


def fetch_local_daily(symbol):
    return local_tdx_reader.daily(symbol=symbol)


def fetch_local_plus_real(symbol, period_enum, req_real=1):
    base_period_enum = period_enum
    match period_enum:
        case PeriodEnum.F15:
            base_period_enum = PeriodEnum.F5
        case PeriodEnum.F30:
            base_period_enum = PeriodEnum.F5
        case PeriodEnum.W:
            base_period_enum = PeriodEnum.D

    df = fetch_local_data(symbol, base_period_enum)
    if req_real:
        if minutes := minutes_since_open():
            match base_period_enum:
                case PeriodEnum.D:
                    offset = 1
                case PeriodEnum.F1:
                    offset = minutes
                case _:
                    offset = minutes / 5

            real_time_df = fetch_real(symbol, base_period_enum, offset)
            if period_enum == PeriodEnum.D:
                real_time_df = real_time_df[real_time_df.index.date > df.index[-1].date()]
            else:
                real_time_df = real_time_df[real_time_df.index > df.index[-1]]
            df = pd.concat([df, real_time_df[['open', 'high', 'low', 'close', 'amount', 'volume']]], axis=0)

    if period_enum in [PeriodEnum.F15, PeriodEnum.F30, PeriodEnum.W]:
        df = resample_kline(df, period_enum)

    return df


def read_local_csv(csv_file):
    df = pd.read_csv(csv_file, parse_dates=['datetime'], index_col='datetime')
    df.rename(columns={
        'datetime': 'time',
        'vol': 'volume',
    }, inplace=True)

    return df


def fetch_local_history(date_str, symbol, period_enum):
    date_object = datetime.strptime(date_str, "%Y-%m-%d")
    if period_enum == PeriodEnum.D or date_object >= datetime(2023, 9, 1):
        return fetch_local_plus_real(symbol, period_enum)

    csv_file = f"{config['local_kline_1min_path']}/{date_object.year}_yssj/{symbol}.csv"
    if not os.path.exists(csv_file):
        return fetch_local_plus_real(symbol, period_enum)

    df = read_local_csv(csv_file)
    if date_object.month <= 3:
        csv_file = f"{config['local_kline_1min_path']}/{date_object.year - 1}_yssj/{symbol}.csv"
        if os.path.exists(csv_file):
            df2 = read_local_csv(csv_file)
            df = pd.concat([df2, df])
    if date_object.month >= 9:
        csv_file = f"{config['local_kline_1min_path']}/{date_object.year + 1}_yssj/{symbol}.csv"
        if os.path.exists(csv_file):
            df2 = read_local_csv(csv_file)
            df = pd.concat([df, df2])

    if period_enum in [PeriodEnum.F5, PeriodEnum.F15, PeriodEnum.F30]:
        df = resample_kline(df, period_enum)

    return df


trade_date_list = fetch_local_daily(symbol='999999').reset_index()

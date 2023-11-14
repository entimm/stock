import datetime
import math

import pandas as pd
from flask import render_template, Blueprint
from mootdx.quotes import Quotes
from mootdx.reader import Reader

blueprint = Blueprint('index', __name__)


def minutes_since_open():
    now = datetime.datetime.now()

    target = datetime.datetime(now.year, now.month, now.day, 9, 30)

    diff = now - target

    return diff.total_seconds() // 60


@blueprint.route('/')
def index():
    tdx_dir = '/Volumes/[C] Windows 11/Apps/通达信金融终端(开心果整合版)V2023.03'
    reader = Reader.factory(market='std', tdxdir=tdx_dir)

    df = reader.fzline(symbol='600519')

    client = Quotes.factory(market='std')
    real_time_df = client.bars(symbol='600519', frequency=0, offset=math.ceil(minutes_since_open() / 5.0))

    df = pd.concat([df, pd.DataFrame(real_time_df)], axis=0)

    print(df)

    kline_list = []
    for index, row in df.iterrows():
        kline_list.append({
            'timestamp': index.strftime("%Y-%m-%d %H:%M:%S"),
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'close': row['close'],
            'amount': row['amount'],
            'volume': row['volume'],
        })

    return render_template('index.html', kline_list=kline_list)

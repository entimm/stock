from flask import render_template, Blueprint
from mootdx.reader import Reader

blueprint = Blueprint('index', __name__)


@blueprint.route('/')
def index():
    tdx_dir = '/Volumes/[C] Windows 11/Apps/通达信金融终端(开心果整合版)V2023.03'
    reader = Reader.factory(market='std', tdxdir=tdx_dir)

    df = reader.fzline(symbol='999999')

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

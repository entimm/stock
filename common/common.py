import configparser
import os
from enum import Enum, auto

config = configparser.ConfigParser()
config.read('config.ini')

APP_PATH = os.path.dirname(os.path.dirname(__file__))

RESOURCES_PATH = os.path.join(APP_PATH, 'resources')

STOCK_META_FILE_PATH = os.path.join(RESOURCES_PATH, 'a_stock_meta_list.csv')
NORTH_FUNDS_FILE_PATH = os.path.join(RESOURCES_PATH, 'north_funds.csv')
GNBK_FILE_PATH = os.path.join(RESOURCES_PATH, 'gnbk_list.csv')
ETF_FILE_PATH = os.path.join(RESOURCES_PATH, 'etf.csv')
INDEX_FILE_PATH = os.path.join(RESOURCES_PATH, 'index.csv')

PROCESSED_PATH = os.path.join(RESOURCES_PATH, 'new_processed')
RAW_PATH = os.path.join(RESOURCES_PATH, 'raw')
TOTAL_PATH = os.path.join(RESOURCES_PATH, 'total')

TDX_PATH = config.get('tdx', 'app_path')
TDX_EXPORT_PATH = TDX_PATH + '/T0002/export'
TDX_BLOCK_NEW_PATH = os.path.join(TDX_PATH, 'T0002', 'blocknew')

TUSHARE_TOKEN = config.get('tushare', 'token')


class PeriodEnum(Enum):
    F1 = auto()
    F5 = auto()
    F15 = auto()
    F30 = auto()
    D = auto()


TDX_FREQUENCY_MAP = {
    PeriodEnum.F1: 8,
    PeriodEnum.F5: 0,
    PeriodEnum.D: 9
}

MENUS = [
    {'name': '行情', 'url': '/chart', 'type': 'system'},
    {'name': '个股趋势图', 'url': '/astock', 'type': 'system'},
    {'name': '个股趋势表', 'url': '/astock_table', 'type': 'system'},
    {'name': '概念板块趋势图', 'url': '/gnbk', 'type': 'system'},
    {'name': '概念板块趋势表', 'url': '/gnbk_table', 'type': 'system'},
    {'name': '自选表', 'url': '/diybk_history?bk_key=zxg', 'type': 'system'},
    {'name': '自定义板块表', 'url': '/diybk', 'type': 'system'},
    {'name': '涨跌停表', 'url': '/limited', 'type': 'system'},
    {'name': 'ipo趋势图', 'url': '/ipo', 'type': 'system'},
    {'name': '北向资金', 'url': '/north_funds', 'type': 'system'},
    {'name': 'A股交易额', 'url': '/turnover', 'type': 'system'},

    {'name': 'A股热力图', 'url': 'https://www.moomoo.com/hans/heatmap-cn/stock', 'type': 'external'},
    {'name': '选股宝', 'url': 'https://xuangubao.cn', 'type': 'external'},
    {'name': '选股宝-盯盘', 'url': 'https://xuangubao.cn/dingpan', 'type': 'external'},
    {'name': '选股宝-涨停复盘', 'url': 'https://xuangubao.cn', 'type': 'external'},
    {'name': 'i问财', 'url': 'http://iwencai.com/unifiedwap/home/index', 'type': 'external'},
    {'name': '股票投资管理', 'url': 'https://beyondme.feishu.cn/base/Wdclb8yiaaSOqasOcYycdZV1nxN?table=tbldAfNroUPByq7y&view=vewFGTsFzC', 'type': 'external'},
    {'name': 'TradingView行情', 'url': 'https://cn.tradingview.com/chart/rrCcZSIn/?symbol=SSE:000001', 'type': 'external'},
    {'name': 'TradingView市场', 'url': 'https://cn.tradingview.com/markets/china/', 'type': 'external'},
]

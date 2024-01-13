import datetime
import os
from enum import Enum, auto

from common.config import config

APP_PATH = os.path.dirname(os.path.dirname(__file__))

RESOURCES_PATH = os.path.join(APP_PATH, 'resources')

STOCK_META_FILE_PATH = os.path.join(RESOURCES_PATH, 'a_stock_meta_list.csv')
STOCK_INFO_FILE_PATH = os.path.join(RESOURCES_PATH, 'stock_infos.csv')

NORTH_FUNDS_FILE_PATH = os.path.join(RESOURCES_PATH, 'north_funds.csv')
GNBK_FILE_PATH = os.path.join(RESOURCES_PATH, 'gnbk_list.csv')
ETF_FILE_PATH = os.path.join(RESOURCES_PATH, 'etf.csv')
INDEX_FILE_PATH = os.path.join(RESOURCES_PATH, 'index.csv')

PROCESSED_PATH = os.path.join(RESOURCES_PATH, 'new_processed')
RAW_PATH = os.path.join(RESOURCES_PATH, 'raw')
RAW_V2_PATH = os.path.join(RESOURCES_PATH, 'rawV2')
TOTAL_PATH = os.path.join(RESOURCES_PATH, 'total')

TDX_PATH = config['tdx']['app_path']
TDX_EXPORT_PATH = TDX_PATH + '/T0002/export'
TDX_BLOCK_NEW_PATH = os.path.join(TDX_PATH, 'T0002', 'blocknew')

TUSHARE_TOKEN = config['tushare']['token']
MENUS = config['menus']
DEFAULT_SELECT_OPTIONS = config['default_select_options']

YEAR = datetime.datetime.now().year


class PeriodEnum(Enum):
    F1 = auto()
    F5 = auto()
    F15 = auto()
    F30 = auto()
    D = auto()
    W = auto()


TDX_FREQUENCY_MAP = {
    PeriodEnum.F1: 8,
    PeriodEnum.F5: 0,
    PeriodEnum.D: 9
}

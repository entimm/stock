import datetime
import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

APP_PATH = os.path.dirname(os.path.dirname(__file__))

RESOURCES_PATH = os.path.join(APP_PATH, 'resources')

STOCK_META_FILE_PATH = os.path.join(RESOURCES_PATH, 'a_stock_meta_list.csv')
GNBK_FILE_PATH = os.path.join(RESOURCES_PATH, 'gnbk_list.csv')
ETF_FILE_PATH = os.path.join(RESOURCES_PATH, 'etf.csv')

PROCESSED_PATH = os.path.join(RESOURCES_PATH, 'new_processed')
RAW_PATH = os.path.join(RESOURCES_PATH, 'raw')
TOTAL_PATH = os.path.join(RESOURCES_PATH, 'total')

TDX_PATH = config.get('tdx', 'app_path')
TDX_EXPORT_PATH = TDX_PATH + '/T0002/export'
TDX_BLOCK_NEW_PATH = os.path.join(TDX_PATH, 'T0002', 'blocknew')

YEAR = datetime.datetime.now().year


TUSHARE_TOKEN = config.get('tushare', 'token')

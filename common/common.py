import datetime
import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

APP_PATH = os.path.dirname(os.path.dirname(__file__))

RESOURCES_PATH = os.path.join(APP_PATH, 'resources')

STOCK_META_FILE_PATH = os.path.join(RESOURCES_PATH, 'a_stock_meta_list.csv')
GNBK_FILE_PATH = os.path.join(RESOURCES_PATH, 'gnbk_list.csv')
PROCESSED_PATH = os.path.join(RESOURCES_PATH, 'new_processed')
RAW_PATH = os.path.join(RESOURCES_PATH, 'raw')
TOTAL_PATH = os.path.join(RESOURCES_PATH, 'total')

TDX_DIR = config.get('tdx', 'app_path')
TDX_EXPORT_DIR = TDX_DIR + '/T0002/export'

YEAR = datetime.datetime.now().year


TUSHARE_TOKEN = config.get('tushare', 'token')

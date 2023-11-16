import datetime
import os

APP_PATH = os.path.dirname(os.path.dirname(__file__))

RESOURCES_PATH = os.path.join(APP_PATH, 'resources')

STOCK_META_FILE_PATH = os.path.join(RESOURCES_PATH, 'a_stock_meta_list.csv')
GNBK_FILE_PATH = os.path.join(RESOURCES_PATH, 'gnbk_list.csv')
PROCESSED_PATH = os.path.join(RESOURCES_PATH, 'new_processed')
RAW_PATH = os.path.join(RESOURCES_PATH, 'raw')
TOTAL_PATH = os.path.join(RESOURCES_PATH, 'total')

TDX_DIR = '/Volumes/[C] Windows 11/Apps/通达信金融终端(开心果整合版)V2023.03'
TDX_EXPORT_DIR = TDX_DIR + '/T0002/export'

YEAR = datetime.datetime.now().year


TUSHARE_TOKEN = 'a2cc6ae6dfeb3c9123e9994fa2f1b68ae394d8e4c923c7a3a5867b1e'

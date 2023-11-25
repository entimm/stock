import yaml

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

TDX_PATH = config['tdx']['app_path']
TUSHARE_TOKEN = config['tushare']['token']
MENUS = config['menus']
DEFAULT_SELECT_OPTIONS = config['default_select_options']

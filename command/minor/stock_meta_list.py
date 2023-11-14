import os

import tushare as ts

pro = ts.pro_api('a2cc6ae6dfeb3c9123e9994fa2f1b68ae394d8e4c923c7a3a5867b1e')

# 拉取数据
df = pro.stock_basic(**{
    'ts_code': '',
    'name': '',
    'exchange': '',
    'market': '',
    'is_hs': '',
    'list_status': '',
    'limit': '',
    'offset': ''
}, fields=[
    'ts_code',
    'symbol',
    'name',
    'area',
    'industry',
    'market',
    'list_date'
])

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

df.to_csv(os.path.join(root_path, 'resources', 'stock_meta_list.csv'), index=False)

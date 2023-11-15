import os

import tushare as ts
import datetime

# 设置 tushare token
ts.set_token('a2cc6ae6dfeb3c9123e9994fa2f1b68ae394d8e4c923c7a3a5867b1e')

# 初始化 tushare pro_api
pro = ts.pro_api()

resources_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources', 'total')

# 获取当前日期
current_date = datetime.datetime.now().strftime('%Y%m%d')

# 设定起始日期
start_date = '20110101'

# 循环获取数据并保存到CSV文件
while current_date > start_date:
    # 获取数据
    df = pro.daily(trade_date=current_date)

    # 生成保存文件的路径，这里使用日期作为文件名
    file_path = os.path.join(resources_path, f'data_{current_date}.csv')

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            line_count = sum(1 for line in file)
            if line_count > 1000:
                break

    # 保存数据到CSV文件
    df.to_csv(file_path, index=False)

    # 输出提示信息
    print(f'Data for {current_date} saved to {file_path}')

    # 更新日期为前一天
    current_date = (datetime.datetime.strptime(current_date, '%Y%m%d') - datetime.timedelta(days=1)).strftime('%Y%m%d')
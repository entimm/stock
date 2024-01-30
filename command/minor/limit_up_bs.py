import os

import click
import pandas as pd

from common.const import TOTAL_PATH, RESOURCES_PATH
from common.quotes import trade_date_list

XUANGUBAO_DETAIL_PATH = os.path.join(RESOURCES_PATH, 'xuangubao/details')


@click.command()
def limit_up_bs():
    result = []
    holding = []

    to_buy_list = []
    date_index = 0
    pre_ts = None
    date_list = trade_date_list['date'].tail(500).to_list()
    for ts in date_list:
        date = ts.strftime('%Y%m%d')
        date2 = ts.strftime('%Y-%m-%d')
        csv_file = os.path.join(TOTAL_PATH, f'data_{date}.csv')
        if not os.path.exists(csv_file): continue
        df = pd.read_csv(csv_file)
        df = df[df['ts_code'].str.endswith(('SH', 'SZ'))]
        df['ts_code'] = df['ts_code'].str[:6]

        pre_limit_up_infos = {}
        if pre_ts:
            file_path = os.path.join(XUANGUBAO_DETAIL_PATH, f'detail-{pre_ts.strftime("%Y%m%d")}.csv')
            df_pre_limit_up_infos = pd.read_csv(file_path, index_col="symbol")
            df_pre_limit_up_infos = df_pre_limit_up_infos[['stock_chi_name', 'limit_up_days', 'm_days_n_boards_days', 'm_days_n_boards_boards']]
            df_pre_limit_up_infos.index = df_pre_limit_up_infos.index.astype(str).str[:6]
            pre_limit_up_infos = df_pre_limit_up_infos.to_dict(orient='index')

        # 卖操作
        plan_sell_symbols = [item['symbol'] for item in holding]
        df_to_sell = df[df['ts_code'].isin(plan_sell_symbols)]
        for index, row in df_to_sell.iterrows():
            # 最后一天强制执行以便统计数据
            if len(date_list) - 1 > date_index:
                # 跌停卖不了
                if row['high'] == row['low'] and row['pct_chg'] <= -9.8:
                    continue
                # 涨停就不卖
                if row['high'] == row['low'] and row['pct_chg'] >= 9.8:
                    continue
                # 这种基本也卖不出去
                if (1 - (row['low'] / row['high'])) * 100 <= 1 and row['pct_chg'] <= -9.8:
                    continue

            for target_hold in holding:
                if target_hold['symbol'] == row['ts_code']:
                    holding.remove(target_hold)
                    profit = round((row['open'] / target_hold['buy_price'] - 1) * 100, 2)
                    days = date_index - target_hold['buy_index']

                    if days == 1 and 10 > profit > -10:
                        continue

                    result.append({
                        'symbol': row['ts_code'],
                        'buy_date': target_hold['buy_date'],
                        'buy_price': target_hold['buy_price'],
                        'sell_price': row['open'],
                        'sell_date': date2,
                        'profit': profit,
                        'days': days,
                        'mode': target_hold['mode'],
                        'const_num': target_hold['const_num'],
                        'const_density': target_hold['const_density'],
                    })

        # 买操作
        df_to_buy = df[df['ts_code'].isin(to_buy_list)]
        for index, row in df_to_buy.iterrows():
            # 涨停买不了
            if row['high'] == row['low'] and row['pct_chg'] >= 9.8:
                continue
            # 封死的跌停也不会买
            if row['high'] == row['low'] and row['pct_chg'] <= -9.8:
                continue

            pre_limit_up_info = get_pre_limit_up_info(pre_limit_up_infos, row['ts_code'])
            holding.append({
                'symbol': row['ts_code'],
                'buy_date': date2,
                'buy_price': row['open'],
                'buy_index': date_index,
                'mode': '开盘竞价',
                'close_price': row['close'],
                'const_num': pre_limit_up_info[0],
                'const_density': pre_limit_up_info[1],
            })

        df_hit_limit = df[(df['high'] / df['pre_close'] - 1) * 100 >= 9.8]
        df_hit_limit = df_hit_limit[df_hit_limit['high'] != df_hit_limit['low']]
        for index, row in df_hit_limit.iterrows():
            highest_percent = (row['high'] / row['pre_close'] - 1) * 100
            is_percent_20cm = row['ts_code'][0: 2] in ['68', '30']
            if (is_percent_20cm and highest_percent >= 19.6) or not is_percent_20cm:
                pre_limit_up_info = get_pre_limit_up_info(pre_limit_up_infos, row['ts_code'])
                holding.append({
                    'symbol': row['ts_code'],
                    'buy_date': date2,
                    'buy_price': row['high'],
                    'buy_index': date_index,
                    'mode': '打板',
                    'close_price': row['close'],
                    'const_num': pre_limit_up_info[0],
                    'const_density': pre_limit_up_info[1],
                })

        df = df[df['high'] == df['close']]
        df = df[df['pct_chg'] >= 9.8]
        to_buy_list = df['ts_code'].to_list()

        date_index += 1
        pre_ts = ts

    for target_hold in holding:
        profit = round((target_hold['close_price'] / target_hold['buy_price'] - 1) * 100, 2)
        if 10 > profit > -10:
            continue

        result.append({
            'symbol': target_hold['symbol'],
            'buy_date': target_hold['buy_date'],
            'buy_price': target_hold['buy_price'],
            'sell_price': target_hold['close_price'],
            'sell_date': pre_ts.strftime('%Y-%m-%d'),
            'profit': profit,
            'days': 0,
            'mode': target_hold['mode'],
            'const_num': target_hold['const_num'],
            'const_density': target_hold['const_density'],
        })

    df = pd.DataFrame(result)
    file_path = os.path.join(RESOURCES_PATH, f'limit_up_bs.csv')
    df.to_csv(file_path, index=False)


def get_pre_limit_up_info(pre_limit_up_infos, symbol):
    pre_limit_up_info = pre_limit_up_infos.get(symbol, {})

    const_num = 0
    const_density = 0
    if pre_limit_up_info:
        const_num = pre_limit_up_info.get('limit_up_days', 0)
        if pre_limit_up_info.get('m_days_n_boards_days'):
            const_density = '{}天{}板'.format(pre_limit_up_info.get('m_days_n_boards_days'), pre_limit_up_info.get('m_days_n_boards_boards'))
        else:
            const_density = '首板'

    return const_num, const_density

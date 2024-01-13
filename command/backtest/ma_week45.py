import json
import os

import click

from common.const import RESOURCES_PATH, PeriodEnum
from common.price_calculate import ma
from common.quotes import fetch_local_plus_real


@click.command()
@click.argument('period', type=str, default='D')
@click.argument('symbol', type=str)
def backtest_ma_week45(period: str, symbol):
    strategy = Strategy()
    strategy.run(symbol, PeriodEnum[period])


class Strategy:
    def __init__(self):
        self.symbol = None
        self.period_enum = None

        self.is_plan_sell = False
        self.is_plan_buy = False

        self.buy_ts = None

        self.order_list = []

        self.ma = [45]

    def run(self, symbol, period_enum: PeriodEnum):
        """
        主控制
        """
        self.symbol = symbol
        self.period_enum = period_enum

        df = self.prepare_data_df()

        for index, row in df.iterrows():
            row = row.to_dict()
            self.run_step(index, row)

        # 结果输出
        result_json_file = os.path.join(RESOURCES_PATH, 'backtest', f'back_test_{self.symbol}.json')
        with open(result_json_file, 'w') as json_file:
            json.dump(self.order_list, json_file)

        print('打开浏览器查看回测结果 http://127.0.0.1:8888/backtest_result?symbol={}&period={}&ma={}'.
              format(self.symbol, self.period_enum.name, ','.join(map(str, self.ma))))

    def prepare_data_df(self):
        """
        准备数据
        """
        df = fetch_local_plus_real(self.symbol, self.period_enum)

        for item in self.ma:
            df[f'ma{item}'] = ma(df, item)

        df = df.reset_index(names='date')
        df['time'] = df['date'].dt.strftime('%Y-%m-%d')

        return df

    def run_step(self, index, row):
        """
        逐根K线判断
        """
        # 执行卖出计划
        if self.buy_ts and self.is_plan_sell:
            self.sell(row['date'], row['open'])

        if (not self.buy_ts) and self.is_plan_buy:
            self.buy(row['date'], row['close'])

        # 做计划
        self.make_plan(row)

    def make_plan(self, row):
        # 死叉卖，维护基准价格
        if not self.buy_ts and self.can_buy(row):
            self.is_plan_buy = True

        if self.buy_ts:
            # 金叉后遇到顶分型
            if self.can_sell(row):
                self.is_plan_sell = True

    @staticmethod
    def can_buy(row):
        return row['close'] >= row['ma45']

    @staticmethod
    def can_sell(row):
        return row['close'] < row['ma45']

    def buy(self, ts, price):
        buy_info = {
            'date': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': self.symbol,
            'price': round(price, 2),
            'action': 'BUY',
        }
        print(buy_info)
        self.order_list.append(buy_info)
        self.buy_ts = ts
        self.is_plan_buy = False

    def sell(self, ts, price):
        sell_info = {
            'date': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': self.symbol,
            'price': round(price, 2),
            'action': 'SELL',
        }
        print(sell_info)
        self.order_list.append(sell_info)
        self.buy_ts = None
        self.is_plan_sell = False

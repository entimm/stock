import json
import os

import click
from chan.chan_const import FractalType
from chan.element.bar import Bar
from chan.element.kline import Kline
from chan.manager.bar_union_manager import BarUnionManager

from common.cmd_utils import get_forex_kline
from common.common import RESOURCES_PATH, PeriodEnum
from common.price_calculate import ma, ma_angle


@click.command()
@click.argument('period', type=str, default='D')
@click.argument('symbol', type=str)
def backtest_three_ma_forex(period: str, symbol):
    strategy = Strategy()
    strategy.run(symbol, PeriodEnum[period])


class Strategy:
    def __init__(self):
        self.period_enum = None
        self.bar_union_manager = BarUnionManager()

        self.is_plan_sell = False
        self.is_plan_buy = False

        self.buy_ts = None
        self.buy_base_price = None
        self.sell_base_price = None
        self.sell_flag = 0

        self.lower_fractal = None

        self.order_list = []

        self.last_buy_ma5 = None

    def run(self, symbol, period_enum: PeriodEnum):
        self.symbol = symbol
        self.period_enum = period_enum

        df = get_forex_kline(self.symbol, self.period_enum)

        df['ma5'] = ma(df, 5)
        df['ma15'] = ma(df, 15)
        df['ma60'] = ma(df, 60)
        df['ma60_angle'] = ma_angle(df, 'ma60')
        df['ma432'] = ma(df, 432)
        df['ma432_angle'] = ma_angle(df, 'ma432')
        df['cross'] = df['ma15'] > df['ma60']
        df = df.reset_index(names='date')
        df['time'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        for index, row in df.iterrows():
            row = row.to_dict()

            # 执行卖出计划
            if self.buy_ts and self.is_plan_sell:
                self.sell(row['date'], row['open'])

            if (not self.buy_ts) and self.is_plan_buy:
                # 当天最低价高于基准价就执行买入计划
                if row['low'] >= self.buy_base_price:
                    self.buy(row['date'], row['close'])
                    self.sell_base_price = self.buy_base_price

            if self.buy_ts:
                # 盘中跌破基准价就卖出
                if row['low'] < self.sell_base_price:
                    self.sell(row['date'], min(self.sell_base_price, row['high']))

            # 做计划
            fractal = self.bar_union_manager.add_bar(Bar(index, Kline(row)))
            self.make_plan(row, fractal)

        # 结果输出
        result_json_file = os.path.join(RESOURCES_PATH, 'backtest', f'back_test_{self.symbol}.json')
        with open(result_json_file, 'w') as json_file:
            json.dump(self.order_list, json_file)

        print(f'打开浏览器查看回测结果 http://127.0.0.1:8888/backtest_result?symbol={self.symbol}&period={self.period_enum.name}')

    def make_plan(self, row, fractal):
        # 金叉后底分型重置
        if row['cross']:
            self.last_buy_ma5 = None
            self.lower_fractal = None

        if fractal and fractal.fractal_type == FractalType.BOTTOM:
            if not self.lower_fractal:
                self.lower_fractal = fractal

            if self.lower_fractal.fractal_value > fractal.fractal_value:
                self.lower_fractal = fractal

            # 死叉卖，维护基准价格
            if not self.buy_ts and (not row['cross']) and self.can_buy(row):
                if self.last_buy_ma5 is None or (self.last_buy_ma5 is not None and row['ma5'] >= self.last_buy_ma5):
                    self.is_plan_buy = True
                    self.buy_base_price = self.lower_fractal.fractal_value
                self.last_buy_ma5 = row['ma5']

        if self.buy_ts:
            # 金叉后遇到顶分型
            if row['cross'] and row['high'] < row['ma60']:
                self.is_plan_sell = True
                self.sell_flag = 1
            # 60均线跌破432均线
            elif self.can_sell1(row):
                self.is_plan_sell = True
                self.sell_flag = 2.1
            # 432均线向下
            # elif self.can_sell2(row):
            #     self.is_plan_sell = True
            #     self.sell_flag = 2.2

    @staticmethod
    def can_buy(row):
        return row['ma432_angle'] > 0 and row['ma60_angle'] > 0.06 and row['ma60'] >= row['ma432'] and row['ma15'] >= row['ma432']

    @staticmethod
    def can_sell1(row):
        return row['ma60'] < row['ma432']

    @staticmethod
    def can_sell2(row):
        return row['ma432_angle'] < 0

    def buy(self, ts, price):
        if (1 - self.buy_base_price / price) * 100 > 0.8:
            return
        buy_info = {
            'date': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': self.symbol,
            'price': round(price, 2),
            'action': 'BUY',
            'out_price': round(self.buy_base_price, 2),
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
            'flag': self.sell_flag,
        }
        print(sell_info)
        self.order_list.append(sell_info)
        self.buy_ts = None
        self.is_plan_sell = False
        self.sell_flag = 0

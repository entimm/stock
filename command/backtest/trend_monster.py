import json
import os
from dataclasses import dataclass
from typing import Optional

import click
import pandas as pd

from common.cmd_utils import get_hfq_kline
from common.common import PROCESSED_PATH, RESOURCES_PATH
from common.quotes import trade_date_list


@click.command()
def backtest_trend_monster():
    strategy = Strategy()
    strategy.run()


@dataclass
class Plan:
    to_sell: bool
    to_buy_stock: str


@dataclass
class Hold:
    stock: str
    buy_ts: Optional[pd.Timestamp]


# 常量
RESULT_JSON_FILE = os.path.join(RESOURCES_PATH, 'back_test.json')
START_DATE = pd.Timestamp('2011-01-01 00:00:00')

class Strategy:
    def __init__(self):
        self.plan = Plan(to_sell=False, to_buy_stock='')
        self.hold = Hold(stock='', buy_ts=None)

        self.order_list = []

    def run(self):
        select_stock_method = self.select_stock_func()
        for ts in self.step_walk():
            # 根据前一天的卖出计划进行卖出
            if self.plan.to_sell:
                self.exec_sell_plan(ts)

            # 根据前一天的买入计划进行买入
            # 判断当前是否有仓位，没有就买票
            if not self.hold.stock and self.plan.to_buy_stock:
                self.exec_buy_plan(ts)

            # 如果当前仓位不是当天买的，且当天已经不及预期了，那么当天尾盘就卖出
            if self.hold.stock and not self.is_ok(self.hold.stock, ts) and ts.date() > self.hold.buy_ts.date():
                self.sell_in_end(ts)

            # 下一天的计划
            target_symbol = select_stock_method(ts)
            self.make_plan(target_symbol, ts)

        # 结果输出
        self.save_result_to_json()

    @staticmethod
    def step_walk():
        for _, ts in trade_date_list['date'].items():
            if ts < START_DATE: continue
            yield ts

    def make_plan(self, target_symbol, ts):
        # 清空计划,这个计划不清空后面有可能会执行老计划，但是诡异的是不清空的话收益却能更高
        self.plan.to_buy_stock = ''
        if self.hold.stock:
            if self.is_ok(target_symbol, ts) and target_symbol != self.hold.stock:
                self.plan.to_sell = True
                self.plan.to_buy_stock = target_symbol
            # 当前的持仓票不及预期就计划第二天早盘卖掉，但是结果更不好，先不做
            # elif not self.is_ok(self.hold.stock, ts):
            #     self.plan.to_sell = True
            return

        if self.is_ok(target_symbol, ts):
            self.plan.to_buy_stock = target_symbol

    def exec_sell_plan(self, ts):
        df_hold = get_hfq_kline(self.hold.stock)
        if ts in df_hold.index:
            self.sell(ts, df_hold.loc[ts].open)

    def exec_buy_plan(self, ts):
        df_buy = get_hfq_kline(self.plan.to_buy_stock)
        df_buy = df_buy[df_buy.index <= ts]
        if ts in df_buy.index:
            # 排除一字板 排除开盘就是最高价的
            if df_buy.loc[ts].low != df_buy.loc[ts].high and df_buy.loc[ts].open != df_buy.loc[ts].high:
                # 开盘价小于6个点
                if ((df_buy.iloc[-1].open / df_buy.iloc[-2].close) - 1) * 100 <= 6:
                    self.buy(ts, df_buy.loc[ts].open)

    def sell_in_end(self, ts):
        df_hold = get_hfq_kline(self.hold.stock)
        if ts in df_hold.index:
            self.sell(ts, df_hold.loc[ts].close)

    @staticmethod
    def is_ok(symbol, ts):
        df = get_hfq_kline(symbol)
        df = df[df.index <= ts]
        if ts in df.index:
            # 当天的收盘价低于前一天的收盘价就是不行
            if df.iloc[-1].close < df.iloc[-2].close:
                return False
        return True

    def buy(self, ts, price):
        buy_info = {
            'date': ts.strftime('%Y%m%d'),
            'symbol': self.plan.to_buy_stock,
            'price': round(price, 2),
            'action': 'BUY',
        }
        print(buy_info)
        self.order_list.append(buy_info)
        self.hold.stock = self.plan.to_buy_stock
        self.hold.buy_ts = ts
        self.plan.to_buy_stock = ''

    def sell(self, ts, price):
        sell_info = {
            'date': ts.strftime('%Y%m%d'),
            'symbol': self.hold.stock,
            'price': round(price, 2),
            'action': 'SELL',
        }
        print(sell_info)
        self.order_list.append(sell_info)
        self.hold.stock = ''
        self.plan.to_sell = False

    @staticmethod
    def select_stock_func():
        stock_poll = {}

        def closure(ts):
            if not stock_poll.get(ts.year):
                csv_file = os.path.join(PROCESSED_PATH, f'{ts.year}-MA5涨1.csv')
                df = pd.read_csv(csv_file)
                stock_poll[ts.year] = {date: item.split('|')[0] for date, item in df.iloc[0].to_dict().items()}

            return stock_poll[ts.year][ts.strftime('%Y%m%d')]

        return closure

    def save_result_to_json(self):
        with open(RESULT_JSON_FILE, 'w') as json_file:
            json.dump(self.order_list, json_file)
#!/usr/bin/env python

import click

from command.cal_new_high import cal_new_high
from command.cal_new_high_freq import cal_new_high_freq
from command.analyze import analyze
from command.backtest.ma_week45 import backtest_ma_week45
from command.convert_astock import convert_astock
from command.convert_gnbk import convert_gnbk, convert_gnbk_trend_up, convert_gnbk_trend_down
from command.download_total import download_total
from command.cal_trend_ptg import cal_trend_ptg
from command.test.convert_tdx_xls import convert_tdx_xls
from command.download_img import download_fs_img, cal_limit_up_trend
from command.hot_lose import hot_lose
from command.kaipanla import kaipanla_mood, kaipanla_limit_up, kaipanla_limit_down, kaipanla_notice
from command.limit_up_bs import limit_up_bs
from command.main_army import main_army_up, main_army_down
from command.market_height import market_height
from command.north_funds import north_funds
from command.stock_meta import stock_meta
from command.test.test import test
from command.xuangubao import download_xuangubao_detail, arrange_xuangubao_detail
from command.mv_raw import mv_raw
from command.backtest.trend_monster import backtest_trend_monster


@click.group()
def main():
    pass


main.add_command(analyze)

main.add_command(convert_astock)
main.add_command(convert_gnbk)
main.add_command(convert_gnbk_trend_up)
main.add_command(convert_gnbk_trend_down)

main.add_command(download_total)
main.add_command(mv_raw)

main.add_command(cal_trend_ptg)
main.add_command(convert_tdx_xls)
main.add_command(stock_meta)
main.add_command(north_funds)

main.add_command(kaipanla_mood)
main.add_command(kaipanla_limit_up)
main.add_command(kaipanla_limit_down)
main.add_command(kaipanla_notice)

main.add_command(download_xuangubao_detail)
main.add_command(arrange_xuangubao_detail)

main.add_command(backtest_trend_monster)
main.add_command(backtest_ma_week45)

main.add_command(hot_lose)
main.add_command(limit_up_bs)
main.add_command(main_army_up)
main.add_command(main_army_down)
main.add_command(market_height)

main.add_command(download_fs_img)
main.add_command(cal_limit_up_trend)

main.add_command(cal_new_high)
main.add_command(cal_new_high_freq)

main.add_command(test)

if __name__ == '__main__':
    main()

#!/usr/bin/env python

import click

from command.analyze import analyze
from command.convert_astock import convert_astock
from command.convert_gnbk import convert_gnbk, convert_gnbk_trend_up, convert_gnbk_trend_down
# from command.autogui.tdx_auto_export import tdx_auto_export_stock
# from command.autogui.tdx_auto_export import tdx_auto_export_gnbk
from command.download_total import download_total
from command.minor.cal_trend_ptg import cal_trend_ptg
from command.minor.convert_tdx_xls import convert_tdx_xls
from command.minor.kaipanla import kaipanla_mood, kaipanla_limit_up, kaipanla_limit_down, kaipanla_notice
from command.minor.north_funds import north_funds
from command.minor.stock_meta import stock_meta
from command.minor.xuangubao import download_xuangubao_plates, download_xuangubao_stock, download_xuangubao_detail, arrange_xuangubao_detail
from command.mv_raw import mv_raw
from command.backtest.trend_monster import backtest_trend_monster
from command.backtest.three_ma import backtest_three_ma
from command.backtest.three_ma_forex import backtest_three_ma_forex


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

# main.add_command(tdx_auto_export_stock)
# main.add_command(tdx_auto_export_gnbk)

main.add_command(cal_trend_ptg)
main.add_command(convert_tdx_xls)
main.add_command(stock_meta)
main.add_command(north_funds)

main.add_command(kaipanla_mood)
main.add_command(kaipanla_limit_up)
main.add_command(kaipanla_limit_down)
main.add_command(kaipanla_notice)

main.add_command(download_xuangubao_plates)
main.add_command(download_xuangubao_stock)
main.add_command(download_xuangubao_detail)
main.add_command(arrange_xuangubao_detail)

main.add_command(backtest_trend_monster)
main.add_command(backtest_three_ma)
main.add_command(backtest_three_ma_forex)

if __name__ == '__main__':
    main()

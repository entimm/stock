import click

# from command.autogui.tdx_auto_export import tdx_auto_export_stock
# from command.autogui.tdx_auto_export import tdx_auto_export_gnbk
from command.download_total import download_total
from command.analyze import analyze
from command.convert_astock import convert_astock
from command.convert_gnbk import convert_gnbk, convert_gnbk_trend_up, convert_gnbk_trend_down
from command.minor.test import test
from command.minor.cal_trend_ptg import cal_trend_ptg
from command.minor.convert_tdx_xls import convert_tdx_xls
from command.minor.north_funds import north_funds
from command.minor.stock_meta import stock_meta
from command.mv_raw import mv_raw


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
main.add_command(test)


if __name__ == '__main__':
    main()

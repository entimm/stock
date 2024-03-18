import click

from common.quotes import trade_date_list


@click.command()
def tip():
    print(trade_date_list['date'].to_list()[-1])

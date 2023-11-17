import os
from pathlib import Path

from mootdx.reader import Reader

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.common import TDX_DIR


reader = Reader.factory(market='std', tdxdir=TDX_DIR)

df = reader.block_new()

print(f'所有自定义板块:{df}')

df = reader.block_new(group=True)

print(df)
print(f'所有自定义板块并分组:{df}')

df = reader.block_new('白马')
print(f'白马:{df}')


def read_zxg():
    zxg_file = os.path.join(TDX_DIR, 'T0002', 'blocknew', 'zxg.blk')

    if not Path(zxg_file).exists():
        raise Exception("file not exists")

    codes = open(zxg_file).read().splitlines()

    return [c[1:] for c in codes if c != ""]


print(f'自选股:{read_zxg()}')
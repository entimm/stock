import datetime
import os
import re
import shutil

import click

from common.common import RAW_PATH, TDX_EXPORT_DIR


def is_recently_created(file_path, threshold_minutes=120):
    creation_time = os.path.getctime(file_path)
    creation_time_datetime = datetime.datetime.fromtimestamp(creation_time)
    current_time = datetime.datetime.now()
    time_difference = current_time - creation_time_datetime

    return time_difference.total_seconds() <= (threshold_minutes * 60)


@click.command()
def mv_raw():
    contents = os.listdir(TDX_EXPORT_DIR)
    for item in contents:
        source_path = os.path.join(TDX_EXPORT_DIR, item)

        file_regex = re.compile(r'(全部Ａ股|行业概念)(\d{6})')

        match = file_regex.match(item)
        if not match:
            continue

        if not is_recently_created(source_path):
            continue

        destination_path = os.path.join(RAW_PATH, match.group(1), item)

        if os.path.exists(destination_path):
            continue

        shutil.move(source_path, destination_path)

        print(source_path)

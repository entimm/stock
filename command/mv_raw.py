import datetime
import os
import re
import shutil


def is_recently_created(file_path, threshold_minutes=120):
    creation_time = os.path.getctime(file_path)
    creation_time_datetime = datetime.datetime.fromtimestamp(creation_time)
    current_time = datetime.datetime.now()
    time_difference = current_time - creation_time_datetime

    return time_difference.total_seconds() <= (threshold_minutes * 60)


TDX_EXPORT_DIR = '/Volumes/[C] Windows 11/Apps/通达信金融终端(开心果整合版)V2023.03/T0002/export'
RESOURCES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
RAW_DIR = os.path.join(RESOURCES_PATH, 'raw')

if __name__ == '__main__':
    contents = os.listdir(TDX_EXPORT_DIR)
    for item in contents:
        source_path = os.path.join(TDX_EXPORT_DIR, item)

        file_regex = re.compile(r'(全部Ａ股|行业概念)(\d{6})')

        match = file_regex.match(item)
        if not match:
            continue

        if not is_recently_created(source_path):
            continue

        destination_path = os.path.join(RESOURCES_PATH, 'raw', match.group(1), item)

        if os.path.exists(destination_path):
            continue

        shutil.move(source_path, destination_path)

        print(source_path)

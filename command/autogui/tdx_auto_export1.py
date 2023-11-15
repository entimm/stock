import os
import time

import click
import pyautogui

from common.common import RESOURCES_PATH, TDX_EXPORT_DIR


def export():
    pyautogui.press('3')
    pyautogui.press('4')
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('enter')
    print('执行导出...')
    time.sleep(5)


def auto_load_next(date_list_filename, cur_line):
    global load_time
    current_timestamp = time.time()
    pyautogui.press(']')
    print(f'按键],加载数据{load_time}...')
    time.sleep(load_time)

    export()

    findfilename = read_nth_line(date_list_filename, cur_line)
    findfilename = '全部Ａ股' + findfilename + '.xls'
    while True:
        print('>>>')
        cost_time = int(time.time() - current_timestamp)
        if is_file_exists(TDX_EXPORT_DIR, findfilename):
            print(f'{findfilename}->SUCCESS({cost_time})')
            pyautogui.press('esc')
            break
        else:
            time.sleep(1)
            if (cost_time >= load_time + 10):
                load_time += 1
                pyautogui.press('esc')
                export()


def is_file_exists(directory, filename):
    return os.path.exists(os.path.join(directory, filename))


def count_lines(filePath):
    with open(filePath, 'r') as file:
        return len(file.readlines())


def read_nth_line(filename, n):
    if n == 0:
        print('cur_line为0了')
        exit()
    with open(filename, 'r') as file:
        for i, line in enumerate(file, 1):
            if i == n:
                return line.strip()


@click.command()
def tdx_auto_export1():
    date_list_filename = os.path.join(RESOURCES_PATH, 'date_from_2018.txt')

    times = 0
    load_time = 20
    cur_line = count_lines(date_list_filename)

    while True:
        findfilename = read_nth_line(date_list_filename, cur_line)
        findfilename = '全部Ａ股' + findfilename + '.xls'
        if is_file_exists(TDX_EXPORT_DIR, findfilename):
            cur_line -= 1
        else:
            break

    findfilename = read_nth_line(date_list_filename, cur_line)
    print(f'findfilename开始值为{findfilename}')

    time.sleep(10)
    print('START！！！')

    while True:
        auto_load_next(date_list_filename, cur_line)
        cur_line -= 1
        times += 1
        print(f'NO.{str(times)}->OK')

        if cur_line == 0:
            print('END！！！')
            exit()

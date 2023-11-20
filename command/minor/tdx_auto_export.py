import os
import time

import click
import pyautogui

from common.common import RESOURCES_PATH, TDX_EXPORT_PATH


def count_lines(file_path):
    with open(file_path, 'r') as file:
        return len(file.readlines())


def is_file_exists(directory, filename):
    return os.path.exists(os.path.join(directory, filename))


def read_nth_line(filename, n):
    if n == 0:
        print('cur_line为0了')
        exit()
    with open(filename, 'r') as file:
        for i, line in enumerate(file, 1):
            if i == n:
                return line.strip()


class tdx_auto_export:
    def __init__(self, name, load_waiting, export_waiting):
        self.name = name
        self.load_waiting = load_waiting
        self.export_waiting = export_waiting

    def export(self):
        pyautogui.press('3')
        pyautogui.press('4')
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('enter')
        print('执行导出...')
        time.sleep(self.export_waiting)

    def auto_load_next(self, date_list_filename, cur_line):
        current_timestamp = time.time()
        pyautogui.press(']')
        print(f'按键],加载数据,等待{self.load_waiting}...')
        time.sleep(self.load_waiting)

        self.export()

        findfilename = read_nth_line(date_list_filename, cur_line)
        findfilename = self.name + findfilename + '.txt'
        while True:
            print('>>>')
            cost_time = int(time.time() - current_timestamp)
            if is_file_exists(TDX_EXPORT_PATH, findfilename):
                print(f'{findfilename}->SUCCESS({cost_time})')
                pyautogui.press('esc')
                break
            else:
                time.sleep(1)
                if cost_time >= self.load_waiting + 10:
                    self.load_waiting += 1
                    pyautogui.press('esc')
                    self.export()

    def tdx_auto_export(self):
        date_list_filename = os.path.join(RESOURCES_PATH, 'date_from_2018.txt')

        times = 0
        cur_line = count_lines(date_list_filename)

        while True:
            findfilename = read_nth_line(date_list_filename, cur_line)
            findfilename = self.name + findfilename + '.txt'
            if is_file_exists(TDX_EXPORT_PATH, findfilename):
                cur_line -= 1
            else:
                break

        findfilename = read_nth_line(date_list_filename, cur_line)
        print(f'findfilename开始值为{findfilename}')

        time.sleep(10)
        print('START！！！')

        while True:
            self.auto_load_next(date_list_filename, cur_line)
            cur_line -= 1
            times += 1
            print(f'NO.{str(times)}->OK')

            if cur_line == 0:
                print('END！！！')
                exit()


@click.command()
def tdx_auto_export_stock():
    export = tdx_auto_export('全部Ａ股', 20, 5)
    export.tdx_auto_export()


@click.command()
def tdx_auto_export_gnbk():
    export = tdx_auto_export('行业概念', 5, 2)
    export.tdx_auto_export()

import os
import time

import click
import pyautogui

from common.common import RESOURCES_PATH, TDX_EXPORT_DIR

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
        global load_time
        current_timestamp = time.time()
        pyautogui.press(']')
        print(f'按键],加载数据{load_time}...')
        time.sleep(load_time)

        self.export()

        findfilename = self.read_nth_line(date_list_filename, cur_line)
        findfilename = self.name + findfilename + '.txt'
        while True:
            print('>>>')
            cost_time = int(time.time() - current_timestamp)
            if self.is_file_exists(TDX_EXPORT_DIR, findfilename):
                print(f'{findfilename}->SUCCESS({cost_time})')
                pyautogui.press('esc')
                break
            else:
                time.sleep(1)
                if (cost_time >= load_time + 10):
                    load_time += 1
                    pyautogui.press('esc')
                    self.export()


    def is_file_exists(self, directory, filename):
        return os.path.exists(os.path.join(directory, filename))


    def count_lines(self, filePath):
        with open(filePath, 'r') as file:
            return len(file.readlines())


    def read_nth_line(self, filename, n):
        if n == 0:
            print('cur_line为0了')
            exit()
        with open(filename, 'r') as file:
            for i, line in enumerate(file, 1):
                if i == n:
                    return line.strip()



    def tdx_auto_export(self):
        date_list_filename = os.path.join(RESOURCES_PATH, 'date_from_2018.txt')

        times = 0
        load_time = self.load_waiting
        cur_line = self.count_lines(date_list_filename)

        while True:
            findfilename = self.read_nth_line(date_list_filename, cur_line)
            findfilename = self.name + findfilename + '.txt'
            if self.is_file_exists(TDX_EXPORT_DIR, findfilename):
                cur_line -= 1
            else:
                break

        findfilename = self.read_nth_line(date_list_filename, cur_line)
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
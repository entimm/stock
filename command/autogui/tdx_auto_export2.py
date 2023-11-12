import pyautogui
import time
import os

import root


def export():
    pyautogui.press('3')
    pyautogui.press('4')
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('enter')
    print("执行导出...")
    time.sleep(2)

def auto_load_next(cur_line):
    global load_time
    current_timestamp = time.time()
    pyautogui.press(']')
    print(f"按键],加载数据{load_time}...")
    time.sleep(load_time)

    export()

    findfilename = read_nth_line(date_list_filename, cur_line)
    findfilename = "行业概念"+findfilename+".txt"
    while True:
        print('>>>')
        cost_time = int(time.time() - current_timestamp)
        if is_file_exists(directory, findfilename):
            print(f"{findfilename}->SUCCESS({cost_time})")
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
        print("cur_line为0了")
        exit()
    with open(filename, 'r') as file:
        for i, line in enumerate(file, 1):
            if i == n:
                return line.strip()

directory = "/Volumes/[C] Windows 11/Apps/通达信金融终端(开心果整合版)V2023.03/T0002/export"
date_list_filename = f'{root.path}/resources/date_from_2018.txt'

times = 0
load_time = 5
cur_line = count_lines(date_list_filename)

while True:
    findfilename = read_nth_line(date_list_filename, cur_line)
    findfilename = "行业概念"+findfilename+".txt"
    if is_file_exists(directory, findfilename):
        cur_line -= 1
    else:
        break

findfilename = read_nth_line(date_list_filename, cur_line)
print(f"findfilename开始值为{findfilename}")

time.sleep(10)
print("START！！！")

while True:
    auto_load_next(cur_line)
    cur_line -= 1
    times += 1
    print(f"NO.{str(times)}->OK")

    if cur_line == 0:
        print("END！！！")
        exit()
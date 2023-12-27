import os
from datetime import datetime

import click
import pandas as pd

from common.common import RESOURCES_PATH
from common.utils import send_request

kaipanla_url = 'https://apphis.longhuvip.com/w1/api/index.php'


@click.command()
def download_kaipanla_data():
    result_list = {}

    file_path = os.path.join(RESOURCES_PATH, f'kaipanla.csv')
    try:
        df = pd.read_csv(file_path, index_col='date')
    except FileNotFoundError:
        df = pd.DataFrame()

    url = f'{kaipanla_url}?Index=0&PhoneOSNew=2&VerSion=5.12.0.9&a=ChangeStatistics&apiv=w34&c=HisHomeDingPan&st=1000'
    data_dict = send_request(url)
    if data_dict['errcode'] != '0':
        print('ChangeStatistics接口请求错误')
        exit()
    market_mood_list = {entry["Day"]: entry for entry in data_dict['info']}

    cur_day = datetime.now().strftime("%Y-%m-%d")
    del market_mood_list[cur_day]
    for day in list(market_mood_list.keys())[::-1]:
        if day in df.index:
            continue
        info = {}
        url = f'{kaipanla_url}?Day={day}&PhoneOSNew=2&VerSion=5.12.0.9&a=HisZhangFuDetail&apiv=w34&c=HisHomeDingPan'
        data_dict = send_request(url)
        if data_dict['errcode'] != '0':
            print(f'HisZhangFuDetail接口请求错误, day={day}')
            exit()

        info['date'] = day
        info['strong'] = market_mood_list[day]['strong']
        info['highest_limit'] = market_mood_list[day]['lbgd']
        info['big_noodle'] = market_mood_list[day]['df_num']

        info['down_limit_num'] = data_dict['info']['SJDT']
        info['up_limit_num'] = data_dict['info']['SJZT']
        info['st_down_limit_num'] = data_dict['info']['STDT']
        info['st_up_limit_num'] = data_dict['info']['STZT']
        info['up_num'] = data_dict['info']['SZJS']
        info['down_num'] = data_dict['info']['XDJS']
        info['total_amount'] = data_dict['info']['qscln']

        url = f'{kaipanla_url}?Day={day}&PhoneOSNew=2&VerSion=5.12.0.9&a=ZhangTingExpression&apiv=w34&c=HisHomeDingPan'
        data_dict = send_request(url)
        if data_dict['errcode'] != '0':
            print(f'ZhangTingExpression接口请求错误, day={day}')
            exit()

        info['b1_num'] = data_dict['info'][0]
        info['b2_num'] = data_dict['info'][1]
        info['b3_num'] = data_dict['info'][2]
        info['bn_num'] = data_dict['info'][3]
        info['p_1t2'] = data_dict['info'][4]
        info['p_2t3'] = data_dict['info'][5]
        info['p_3t4'] = data_dict['info'][6]
        info['today_broke_ptg'] = data_dict['info'][7]
        info['yesterday_limit_up_cptg'] = data_dict['info'][8]
        info['yesterday_constant_cptg'] = data_dict['info'][9]
        info['yesterday_broke_cptg'] = data_dict['info'][10]

        result_list[day] = info
        print(result_list[day])

    df_append = pd.DataFrame(list(result_list.values()))
    df = pd.concat([df.reset_index(), df_append], axis=0)
    df.to_csv(file_path, index=False)

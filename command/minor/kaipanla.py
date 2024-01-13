import json
import os
from datetime import datetime

import click
import pandas as pd
import requests
import urllib3

from common.const import RESOURCES_PATH
from common.quotes import trade_date_list

kaipanla_url = 'https://apphis.longhuvip.com/w1/api/index.php'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.command()
def kaipanla_mood():
    result_list = {}

    file_path = os.path.join(RESOURCES_PATH, f'kaipanla.csv')
    try:
        df = pd.read_csv(file_path, index_col='date')
    except FileNotFoundError:
        df = pd.DataFrame()

    url = f'{kaipanla_url}?Index=0&PhoneOSNew=2&VerSion=5.12.0.9&a=ChangeStatistics&apiv=w34&c=HisHomeDingPan&st=1000'
    print(url)
    data_dict = send_request(url)
    if data_dict['errcode'] != '0':
        print('ChangeStatistics接口请求错误')
        exit()
    market_mood_list = {entry["Day"]: entry for entry in data_dict['info']}

    cur_day = datetime.now().strftime("%Y-%m-%d")
    market_mood_list.pop(cur_day, None)
    for day in list(market_mood_list.keys())[::-1]:
        if day in df.index:
            continue
        info = {}
        url = f'{kaipanla_url}?Day={day}&PhoneOSNew=2&VerSion=5.12.0.9&a=HisZhangFuDetail&apiv=w34&c=HisHomeDingPan'
        print(url)
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
        print(url)
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


@click.command()
def kaipanla_limit_up():
    for ts in trade_date_list.tail(100)['date'].to_list():
        day = ts.strftime('%Y-%m-%d')
        file_path = os.path.join(RESOURCES_PATH, 'kaipanla', 'limit_up', f'{day}.csv')
        if os.path.exists(file_path):
            continue

        url = '{}?Day={}&Filter=0&FilterGem=0&FilterMotherboard=0&FilterTIB=0&Index={}&Is_st=1&Order=1&PhoneOSNew=2&PidType=1&Type=9&VerSion=5.12.0.9&a=HisDaBanList&apiv=w34&c=HisHomeDingPan&st={}'
        stock_list = request_kaipanla_page_data(url, day, 0, 50, 'list')
        stock_list = [{
            'symbol': item[0],  # 股票代码
            'name': item[1],  # 股票名称
            'limit_ts': item[6],  # 封停时间戳
            'limit_amount': item[8],  # 封单
            'const_desc': item[9],  # 连板描述
            'const_num': item[10],  # 连板数
            'block': item[11],  # 板块
            'master_net_amount': item[12],  # 主力净额
            'amount': item[13],  # 成交额
            'act_turnover': item[14],  # 实际换手
            'act_flow_amount': item[15],  # 实际流通
            'reason': item[16],  # 涨停原因
            'max_limit_amount': item[23],  # 最大封单
            'last_limit_ts': item[25],  # 最后封停时间戳
            'together_num': item[27],  # 一起涨停数
        } for item in stock_list]

        if not stock_list:
            continue

        df = pd.json_normalize(stock_list)
        df.to_csv(file_path, index=False)


@click.command()
def kaipanla_limit_down():
    for ts in trade_date_list.tail(100)['date'].to_list():
        day = ts.strftime('%Y-%m-%d')
        file_path = os.path.join(RESOURCES_PATH, 'kaipanla', 'limit_down', f'{day}.csv')
        if os.path.exists(file_path):
            continue

        url = '{}?Day={}&Filter=0&FilterGem=0&FilterMotherboard=0&FilterTIB=0&Index={}&Is_st=1&Order=1&PhoneOSNew=2&PidType=3&Type=6&VerSion=5.12.0.9&a=HisDaBanList&apiv=w34&c=HisHomeDingPan&st={}'
        stock_list = request_kaipanla_page_data(url, day, 0, 50, 'list')
        stock_list = [{
            'symbol': item[0],  # 股票代码
            'name': item[1],  # 股票名称
            'limit_ts': item[6],  # 封停时间戳
            'limit_amount': item[8],  # 封单
            'block': item[11],  # 板块
            'master_net_amount': item[12],  # 主力净额
            'amount': item[13],  # 成交额
            'act_turnover': item[14],  # 实际换手
            'act_flow_amount': item[15],  # 实际流通
        } for item in stock_list]

        if not stock_list:
            continue

        df = pd.json_normalize(stock_list)
        df.to_csv(file_path, index=False)


def request_kaipanla_page_data(url_template, day, index, page_size, list_field):
    url = url_template.format(kaipanla_url, day, index, page_size)
    print(url)
    data_dict = send_request(url)
    if data_dict['errcode'] != '0':
        print(f'HisDaBanList接口请求错误, day={day}')
        exit()

    data_list = data_dict[list_field]

    if len(data_dict[list_field]) == page_size:
        data_list.extend(request_kaipanla_page_data(url_template, day, index + 50, page_size, list_field))

    return data_list


@click.command()
def kaipanla_notice():
    for ts in trade_date_list.tail(100)['date'].to_list():
        day = ts.strftime('%Y-%m-%d')

        file_path = os.path.join(RESOURCES_PATH, 'kaipanla/notice', f'notice_{day}.json')
        if os.path.exists(file_path):
            continue

        url = '{}/w1/api/index.php?Date={}&Index={}&PhoneOSNew=2&VerSion=5.12.0.9&a=GetPMSL_PMLD&apiv=w34&c=FuPanLa&st={}'
        data_list = request_kaipanla_page_data(url, day, 0, 50, 'List')

        if not data_list:
            continue

        with open(file_path, 'w') as json_file:
            json.dump(data_list, json_file)


def send_request(url):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'lhb/5.12.9 (com.kaipanla.www; build:0; iOS 17.1.2) Alamofire/5.12.9',
        'Accept-Language': 'zh-Hans-CN;q=1.0',
    }

    response = requests.get(url, headers=headers, verify=False)
    return json.loads(response.text)

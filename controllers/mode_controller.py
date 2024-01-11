import os

from flask import Blueprint, render_template, request

from app_cache import cache
from common.common import RAW_V2_PATH
from common.tdx import read_tdx_text
from common.utils import filter_files_by_date
from controllers import make_cache_key

blueprint = Blueprint('follow_bull', __name__)


def mode_shrink_adj(df):
    df = df[df['上次涨停'] <= 10]
    df = df[df['连缩量'] >= 1]
    df = df[df['涨幅%'] < 0]

    return df


def mode_follow_bull(df):
    df = df[df['上次涨停'] <= 10]
    df = df[df['连放量'] == 1]
    df = df[df['昨涨幅'] < 0]
    df = df[df['涨幅%'] > abs(df['昨涨幅'])]
    df = df[~((df['涨停10D'] == 1) & (df['是否涨停'] == 1))]

    return df


def mode_cont_limited_up(df):
    df = df[df['连板榜'] >= 2]
    df = df.sort_values(by='连板榜', ascending=False)
    return df


def mode_first_limited_up(df):
    df = df[df['首板'] == 1]

    return df

def mode_bomb_limit(df):
    df = df[df['炸板'] == 1]

    return df


@blueprint.route('/mode')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def mode():
    mode_list: list = [
        ('次阳', mode_follow_bull,),
        ('缩调', mode_shrink_adj,),
        ('连板', mode_cont_limited_up,),
        ('首板', mode_first_limited_up,),
        ('炸板', mode_bomb_limit,),
    ]
    mode = request.args.get('mode', 0, type=int)
    directory_path = os.path.join(RAW_V2_PATH, '全部Ａ股')
    file_pattern = r'(\d{8})'
    file_pattern = f'全部Ａ股({file_pattern}).txt'

    file_list = filter_files_by_date(directory_path, file_pattern)
    file_list = sorted(file_list, key=lambda x: x[1], reverse=True)
    file_list = file_list[0:30]

    result_dict = {}

    mode_call = mode_list[mode][1]
    for file_path, date in file_list:
        if not os.path.exists(file_path): continue
        df = read_tdx_text(file_path)
        df = mode_call(df)
        df = df.sort_values(by='MA5涨1', ascending=False)
        df['show'] = df['名称'].astype(str) + '|' + df['代码'].astype(str) + '|' + df['涨幅%'].astype(str) + '|' + df['MA5涨1'].astype(str)
        result_dict[f"{date[:4]}-{date[4:6]}-{date[6:]}"] = df['show'].to_list()

    template_var = {
        'data': dict(result_dict.items()),
        'mode_list': [item[0] for item in mode_list],
        'request_args': {
            'mode': mode,
            'socket_token': request.args.get('socket_token', '', str),
        }
    }

    return render_template('mode.html', **template_var)

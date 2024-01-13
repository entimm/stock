from flask import Blueprint
from pypinyin import pinyin, Style

from app_cache import cache
from common.const import DEFAULT_SELECT_OPTIONS
from common.data import limited_up_total_dict
from common.tdx import stock_info_df
from common.utils import symbol_all
from controllers import make_cache_key

blueprint = Blueprint('info', __name__)


@blueprint.route('/symbol_list')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def symbol_list():
    symbol_all_list = symbol_all()
    for item in symbol_all_list:
        item['pinyin'] = ''.join([item[0] for item in pinyin(item['value'], style=Style.FIRST_LETTER)]).upper()

    return {
        'symbol_all_list': symbol_all_list,
        'default_show_list': DEFAULT_SELECT_OPTIONS,
    }


@blueprint.route('/stock_info/<symbol>')
def stock_info(symbol):
    result = {}
    if symbol in stock_info_df.index:
        result = stock_info_df.loc[symbol].to_json()
    return result


@blueprint.route('/limited_up_info/<symbol>')
def limited_up_info(symbol):
    result = dict(limited_up_total_dict.get(symbol, {}))
    if result:
        result['plates_info'] = []
        for item in result.get('plates', []):
            result['plates_info'].append(f"【{item['plate_name']}({item['count']})】{item.get('plate_reason', '')}")

        result.pop('plates', None)

    return result

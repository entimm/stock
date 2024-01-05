import json
import os

from flask import Blueprint

from app_cache import cache
from common.common import RESOURCES_PATH
from common.config import config
from common.quotes import trade_date_list
from controllers import make_cache_key

blueprint = Blueprint('hot_lose', __name__)

JSON_FILE = os.path.join(RESOURCES_PATH, f'hot_lose.json')


@blueprint.route('/hot_lose_data')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def hot_lose_data():
    result = {}
    with open(JSON_FILE, 'r') as file:
        hot_lose_data = json.load(file)
    for ts in trade_date_list.tail(config.get('table_cols', 200))['date'].to_list():
        date2 = ts.strftime('%Y-%m-%d')
        result[date2] = hot_lose_data.get(date2, [])

    return result

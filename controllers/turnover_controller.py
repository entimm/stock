from flask import Blueprint, render_template

from app_cache import cache
from common.quotes import fetch_local_daily
from controllers import make_cache_key

blueprint = Blueprint('turnover', __name__)


@blueprint.route('/turnover')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def turnover():
    sh_df = fetch_local_daily(symbol='999999').tail(1000)
    sz_df = fetch_local_daily(symbol='399001').tail(1000)
    sh_df['amount'] = ((sh_df['amount'] + sz_df['amount']) / (10 ** 8)).round(2)
    sh_df.index = sh_df.index.astype(str)

    template_var = {
        'data': sh_df['amount'].to_dict(),
    }

    return render_template('turnover.html', **template_var)

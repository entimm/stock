from flask import Blueprint, render_template

from common.data import local_tdx_reader

blueprint = Blueprint('turnover', __name__)


@blueprint.route('/turnover')
def turnover():
    sh_df = local_tdx_reader.daily(symbol='999999').tail(1000)
    sz_df = local_tdx_reader.daily(symbol='399001').tail(1000)
    sh_df['amount'] = ((sh_df['amount'] + sz_df['amount'])/(10**8)).round(2)
    sh_df.index = sh_df.index.astype(str)

    template_var = {
        'data': sh_df['amount'].to_dict(),
    }

    return render_template('turnover.html', **template_var)

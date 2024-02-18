import yaml
from flask import Blueprint, render_template, request

blueprint = Blueprint('loog', __name__)


@blueprint.route('/loog_data')
def loog_data():
    with open('resources/loog.yaml', 'r', encoding='utf-8') as f:
        loog = yaml.safe_load(f)

    result_list = []
    for year, items in loog.items():
        for item in items:
            date, symbol, name = item.split('|')
            result_list.append({
                'year': year,
                'name': name,
                'symbol': symbol,
                'date': date,
            })

    return result_list


@blueprint.route('/loog')
def loog():
    template_var = {
        'request_args': request.args.to_dict(),
    }

    return render_template('loog.html', **template_var)

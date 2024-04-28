from flask import Blueprint, render_template, request

blueprint = Blueprint('logic', __name__)


@blueprint.route('/logic_data')
def logic_data():
    with open('resources/logic.txt', 'r', encoding='utf-8') as f:
        logic_list = f.readlines()

    result_list = []
    for item in logic_list:
        date, symbol, name, tags, desc = item.split('|')
        result_list.append({
            'name': name,
            'symbol': symbol,
            'date': date,
            'tags': tags,
            'desc': desc,
        })

    return result_list


@blueprint.route('/logic')
def logic():
    template_var = {
        'request_args': request.args.to_dict(),
    }

    return render_template('logic.html', **template_var)

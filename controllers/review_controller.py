from flask import Blueprint, render_template, request

blueprint = Blueprint('review', __name__)


@blueprint.route('/review_data')
def review_data():
    with open('resources/review.txt', 'r', encoding='utf-8') as f:
        review_list = f.readlines()

    result_list = []
    for item in review_list:
        date, desc = item.split('|')
        result_list.append({
            'date': date,
            'desc': desc,
        })

    return result_list


@blueprint.route('/review')
def review():
    template_var = {
        'request_args': request.args.to_dict(),
    }

    return render_template('review.html', **template_var)

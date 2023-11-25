from flask import Blueprint, render_template
from collections import defaultdict

from common.config import MENUS

blueprint = Blueprint('index', __name__)


@blueprint.route('/')
def index():
    grouped_menus = defaultdict(list)
    for item in MENUS:
        grouped_menus[item['type']].append(item)
    grouped_menus = dict(grouped_menus)

    return render_template('index.html', **{'grouped_menus': grouped_menus})

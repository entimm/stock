import os
import re

from flask import Blueprint, render_template

from app_cache import cache
from common.const import PUBLIC_PATH
from controllers import make_cache_key

blueprint = Blueprint('images', __name__)


@blueprint.route('/images_data')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def images_data():
    file_list = {}
    file_regex = re.compile(r'.*(\d{4}-\d{2}-\d{2})')
    for root, dirs, files in os.walk(os.path.join(PUBLIC_PATH, 'static/imgs')):
        if match := file_regex.match(root):
            file_list[match.group(1)] = [item for item in files if item[-3:] == 'gif']
            break

    return file_list


@blueprint.route('/images')
def images():
    return render_template('images.html', **{})

from flask import Blueprint, render_template

blueprint = Blueprint('index', __name__)


@blueprint.route('/')
def index():
    template_var = {
        'links': [
            {'name': '个股趋势图', 'url': '/astock'},
            {'name': '个股趋势表', 'url': '/astock_table'},
            {'name': '概念板块趋势图', 'url': '/gnbk'},
            {'name': '概念板块趋势表', 'url': '/gnbk_table'},
            {'name': '自选表', 'url': '/diybk_history?bk_key=zxg'},
            {'name': '自定义板块表', 'url': '/diybk'},
            {'name': '涨跌停表', 'url': '/limited'},
            {'name': 'A股热力图', 'url': 'https://www.moomoo.com/hans/heatmap-cn/stock'},
            {'name': '选股宝', 'url': 'https://xuangubao.cn'},
            {'name': '选股宝-盯盘', 'url': 'https://xuangubao.cn/dingpan'},
            {'name': '选股宝-涨停复盘', 'url': 'https://xuangubao.cn'},
            {'name': 'i问财', 'url': 'http://iwencai.com/unifiedwap/home/index'},
        ]
    }
    return render_template('index.html', **template_var)
from flask import Blueprint, render_template

blueprint = Blueprint('index', __name__)


@blueprint.route('/')
def index():
    template_var = {
        'links': [
            {'name': '个股趋势图', 'url': '/astock', 'type': 'system'},
            {'name': '个股趋势表', 'url': '/astock_table', 'type': 'system'},
            {'name': '概念板块趋势图', 'url': '/gnbk', 'type': 'system'},
            {'name': '概念板块趋势表', 'url': '/gnbk_table', 'type': 'system'},
            {'name': '自选表', 'url': '/diybk_history?bk_key=zxg', 'type': 'system'},
            {'name': '自定义板块表', 'url': '/diybk', 'type': 'system'},
            {'name': '涨跌停表', 'url': '/limited', 'type': 'system'},
            {'name': 'ipo趋势图', 'url': '/ipo', 'type': 'system'},
            {'name': '北向资金', 'url': '/north_funds', 'type': 'system'},

            {'name': 'A股热力图', 'url': 'https://www.moomoo.com/hans/heatmap-cn/stock', 'type': 'external'},
            {'name': '选股宝', 'url': 'https://xuangubao.cn', 'type': 'external'},
            {'name': '选股宝-盯盘', 'url': 'https://xuangubao.cn/dingpan', 'type': 'external'},
            {'name': '选股宝-涨停复盘', 'url': 'https://xuangubao.cn', 'type': 'external'},
            {'name': 'i问财', 'url': 'http://iwencai.com/unifiedwap/home/index', 'type': 'external'},
            {'name': '股票投资管理', 'url': 'https://beyondme.feishu.cn/base/Wdclb8yiaaSOqasOcYycdZV1nxN?table=tbldAfNroUPByq7y&view=vewFGTsFzC', 'type': 'external'},
        ]
    }
    return render_template('index.html', **template_var)

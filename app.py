import os

from flask import Flask, render_template
from flask_socketio import SocketIO

from app_cache import cache
from common.const import MENUS
from common.utils import create_link

app = Flask(__name__, template_folder='web/templates', static_folder='web/public/static')

app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)

socketio = SocketIO(app)

controllers = [
    'index',
    'chart',
    'line',
    'table',
    'diybk',
    'limited',
    'ipo',
    'north_funds',
    'turnover',
    'mode',
    'limited_power',
    'limited_power2',
    'line2',
    'backtest',
    'info',
    'market_mood',
    'trade_history',
    'trade_history2',
    'notice',
    'large_lock',
    'hot_lose',
    'limit_up_bs',
    'new_stock',
    'main_army',
    'market_height',
    'astock_line2',
    'astock_table2',
    'astock_table3',
    'images',
    'loog',
    'new_high',
    'earth2sky',
]

for controller in controllers:
    blueprint = __import__(f'controllers.{controller}_controller', fromlist=['blueprint']).blueprint
    app.register_blueprint(blueprint)


@app.context_processor
def inject_layout_vars():
    return {
        'menus': MENUS,
        'create_link': create_link,
    }


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', **{'error': error}), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html', **{'error': error}), 500


@socketio.on('message_from_client1')
def handle_client1_message(message):
    print('Received message from client1:', message)
    socketio.emit('message_from_client1', message)


@socketio.on('message_from_client2')
def handle_client2_message(message):
    print('Received message from client2:', message)
    socketio.emit('message_from_client2', message)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8888))
    socketio.run(app, debug=os.environ.get("DEBUG", True), host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

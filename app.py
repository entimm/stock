import os

from flask import Flask

from controllers import index_controller, chart_controller, line_controller, table_controller, diybk_controller, \
    limited_controller, ipo_controller, north_funds_controller

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.register_blueprint(index_controller.blueprint)
app.register_blueprint(chart_controller.blueprint)
app.register_blueprint(line_controller.blueprint)
app.register_blueprint(table_controller.blueprint)
app.register_blueprint(diybk_controller.blueprint)
app.register_blueprint(limited_controller.blueprint)
app.register_blueprint(ipo_controller.blueprint)
app.register_blueprint(north_funds_controller.blueprint)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

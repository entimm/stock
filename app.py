from flask import Flask

from controllers import index_controller, line_controller, table_controller

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.register_blueprint(index_controller.blueprint)
app.register_blueprint(line_controller.blueprint)
app.register_blueprint(table_controller.blueprint)

if __name__ == '__main__':
    app.run(debug=True, port=8008)

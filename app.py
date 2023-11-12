from flask import Flask

from controllers.index_controller import blueprint

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(debug=True, port=8008)

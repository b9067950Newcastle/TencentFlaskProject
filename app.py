from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///host.db'
app.config['SQLALCHEMY_ECHO'] = "True"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = "False"
app.config["RECAPTCHA_PUBLIC_KEY"] = "6Lf41H4iAAAAALCDw0esznqOX1-uxAKABhCYQ51_"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6Lf41H4iAAAAALw_t1vVYYcr9fUvBkqR7yjZqCwN"

db = SQLAlchemy(app)

from ping_service.views import ping_service_blueprint

app.register_blueprint(ping_service_blueprint)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.errorhandler(400)
def bad_request(error):
    return render_template("errors/400.html"), 400


@app.errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(405)
def not_allowed(error):
    return render_template("errors/405.html"), 405


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("errors/500.html"), 500


@app.errorhandler(503)
def service_unavailable(error):
    return render_template("errors/503.html"), 503


if __name__ == '__main__':
    app.run()

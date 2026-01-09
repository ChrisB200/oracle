import logging

from flask import Flask
from flask_cors import CORS

from .routes import routes

logging.getLogger("server")


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    app.register_blueprint(routes)

    return app

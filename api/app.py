import os

from flask import Flask
from flask_cors import CORS

from .routes import routes


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    app.register_blueprint(routes)

    return app


def run_flask():
    app = create_app()
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "9001"))
    app.run(host=host, port=port)

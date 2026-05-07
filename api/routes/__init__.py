from flask import Blueprint

from .alfred import alfred

routes = Blueprint("routes", __name__)

routes.register_blueprint(alfred, url_prefix="/alfred")

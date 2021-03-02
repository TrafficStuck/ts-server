"""This module provides initialization of required components."""

import os

from flask import Flask
from flask_cors import CORS

from app import CACHE
from app.views.traffic import traffic_blueprint


def create_app():
    """Create the flask application and initialize it."""
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(traffic_blueprint, url_prefix="/api/v1")
    app_settings = os.environ.get("SERVER_SETTINGS", "app.settings.DevelopmentConfig")
    app.config.from_object(app_settings)

    CACHE.init_app(app)

    return app

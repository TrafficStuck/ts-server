"""This module provides initialization of required components."""

import os
import logging.config
from http import HTTPStatus

from flask import Flask
from flask_cors import CORS

from app import CACHE
from app.views.traffic import traffic_blueprint
from app.views.static import static_blueprint
from app.views.stops import stops_blueprint
from app.views.index import (
    internal_blueprint,
    handle_404,
    handle_405,
    handle_500
)

logging.config.dictConfig({
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s: %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
            "level": "INFO"
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
})


def create_app():
    """Create the flask application and initialize it."""
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(traffic_blueprint, url_prefix="/api/v1")
    app.register_blueprint(static_blueprint, url_prefix="/api/v1")
    app.register_blueprint(stops_blueprint, url_prefix="/api/v1")
    app.register_blueprint(internal_blueprint, url_prefix="/api/v1")

    app.register_error_handler(HTTPStatus.NOT_FOUND, handle_404)
    app.register_error_handler(HTTPStatus.METHOD_NOT_ALLOWED, handle_405)
    app.register_error_handler(HTTPStatus.INTERNAL_SERVER_ERROR, handle_500)

    app_settings = os.environ.get("SERVER_SETTINGS", "app.settings.DevelopmentConfig")
    app.config.from_object(app_settings)

    CACHE.init_app(app)

    return app

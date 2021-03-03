"""This module provides entrypoint for running server application."""

from app import APP_CONFIG
from app.main import create_app


if __name__ == '__main__':
    server = create_app()
    server.run(host=APP_CONFIG.SERVER_HOST, port=APP_CONFIG.SERVER_PORT)

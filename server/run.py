"""This module provides entrypoint for running server application."""

import os

from app.main import create_app


if __name__ == '__main__':
    # TODO: get for config
    host = os.environ.get("SERVER_HOST", "localhost")
    port = os.environ.get("SERVER_PORT", "5000")

    server = create_app()
    server.run(host=host, port=port)

"""This module provides project environment configurations."""

import os


class BaseConfig:
    """Base application configurations."""
    DEBUG = False
    JSON_AS_ASCII = False

    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    STATIC_DIR = os.path.join(ROOT_DIR, "static")

    # Caching
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ["REDIS_URL"]
    CACHE_KEY_PREFIX = "SERVER:"
    CACHE_DEFAULT_TIMEOUT = 300  # 5 min

    # Database
    MONGO_URI = os.environ["MONGO_URI"]
    MONGO_SERVER_TIMEOUT = os.environ.get("MONGO_SERVER_TIMEOUT", 5000)

    # SERVER
    SERVER_HOST = os.environ.get("SERVER_HOST", "localhost")
    SERVER_PORT = os.environ.get("SERVER_PORT", 5555)


class DevelopmentConfig(BaseConfig):
    """Development application configuration."""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """Production application configuration."""

"""This module provides project environment configurations."""

import os


class BaseConfig:
    """Base application configurations."""
    DEBUG = False
    JSON_AS_ASCII = False

    # Caching
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ["REDIS_URL"]
    CACHE_KEY_PREFIX = "SERVER:"
    CACHE_DEFAULT_TIMEOUT = 300  # 5 min


class DevelopmentConfig(BaseConfig):
    """Development application configuration."""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """Production application configuration."""

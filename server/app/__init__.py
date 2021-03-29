"""This module provides initialization of required components."""

import os

import redis
from flask_caching import Cache
from pymongo import MongoClient
from celery import Celery
from celery.schedules import crontab

from app import settings

# Config
APP_MODE = os.environ["APP_MODE"]
APP_CONFIG_NAME = f"{APP_MODE.capitalize()}Config"
APP_CONFIG = getattr(settings, APP_CONFIG_NAME)()

# Redis
CACHE = Cache()
REDIS = redis.from_url(APP_CONFIG.CACHE_REDIS_URL)

# Mongo
MONGO_CLIENT = MongoClient(
    APP_CONFIG.MONGO_URI,
    connect=False,
    serverSelectionTimeoutMS=APP_CONFIG.MONGO_SERVER_TIMEOUT
)
MONGO_DATABASE = MONGO_CLIENT.traffic_stuck

# Celery
CELERY_APP = Celery("TRAFFIC-STUCK-TASKS", broker=APP_CONFIG.CACHE_REDIS_URL)
CELERY_APP.conf.beat_schedule = {
    "collect_gtfs": {
        "task": "app.tasks.collect_traffic",
        "schedule": crontab(minute="*/5"),
    },
    "prepare_static": {
        "task": "app.tasks.prepare_easyway_static",
        "schedule": crontab(minute=0, hour=3),
    },
    "wakeup_server": {
        "task": "app.tasks.wakeup_server",
        "schedule": crontab(minute="*/25"),
    },
}
CELERY_APP.conf.timezone = "Europe/Kiev"
CELERY_APP.conf.imports = ["app.tasks"]

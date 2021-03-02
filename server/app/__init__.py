"""This module provides initialization of required components."""

import os

from flask_caching import Cache
from pymongo import MongoClient


CACHE = Cache()

# Initialize mongo database connection
MONGO_URI = os.environ["MONGO_URI"]
MONGO_SERVER_TIMEOUT = os.environ.get("MONGO_SERVER_TIMEOUT", 5000)
MONGO = MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_SERVER_TIMEOUT)
DATABASE = MONGO.jammed

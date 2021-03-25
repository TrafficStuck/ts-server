"""This modules provides functionality to work with stops data."""
import logging

from pymongo.errors import PyMongoError

from app import MONGO_DATABASE


LOGGER = logging.getLogger(__name__)


class Stops:
    """Class that provides methods for interaction with traffic timeseries."""

    collection = MONGO_DATABASE.stops

    @classmethod
    def get_nearest_stops(cls, latitude, longitude, limit):
        """Retrieve the nearest stops to provided coordinates."""
        try:
            cursor = cls.collection.find(
                filter={"coordinates": {"$near": [latitude, longitude]}},
                projection={"arrivals": 0},
                limit=limit
            )
        except PyMongoError as err:
            LOGGER.error(
                "Couldn't retrieve nearest stops for (%s, %s): %s",
                latitude, longitude, err
            )
            return None

        return list(cursor)

    @classmethod
    def get_stop_by_id(cls, stop_id):
        """Retrieve the stop by provided id"""
        try:
            result = cls.collection.find_one(filter={"_id": stop_id})
        except PyMongoError as err:
            LOGGER.error("Couldn't retrieve stop by id (%s): %s", stop_id, err)
            return None

        if result is None:
            LOGGER.error("Couldn't find stop by id (%s)", stop_id)
            return None

        return result

    @classmethod
    def get_stops_by_name(cls, query, limit):
        """Retrieve the stop by provided id"""
        try:
            cursor = cls.collection.find(
                filter={"$text":{"$search": query}},
                projection={"arrivals": 0},
                limit=limit
            )
        except PyMongoError as err:
            LOGGER.error("Couldn't retrieve stops by name (%s): %s", query, err)
            return None

        return list(cursor)

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
                projection={"arrivals": 0, "_id": 0},
                limit=limit
            )
        except PyMongoError as err:
            LOGGER.error("Couldn't retrieve aggregated timeseries: %s", err)
            return None

        return [dict(x) for x in cursor]

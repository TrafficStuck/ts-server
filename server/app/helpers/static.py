"""This modules provides functionality to work with static easyway data."""

import logging

from pymongo.errors import PyMongoError

from app import MONGO_DATABASE


LOGGER = logging.getLogger(__name__)


class Static:
    """Class that provides methods for interaction with transport static data."""

    collection = MONGO_DATABASE.static

    @classmethod
    def get_static_info(cls, info_id):
        """Retrieve transport static information by id."""
        try:
            result = cls.collection.find_one(filter={"_id": info_id})
        except PyMongoError as err:
            LOGGER.error("Couldn't retrieve static info (%s): %s", info_id, err)
            return None

        if result is None:
            LOGGER.error("Couldn't find static info (%s)", info_id)
            return None

        return result.get("data")

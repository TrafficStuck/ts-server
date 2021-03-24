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
            cursor = cls.collection.find_one(
                filter={"id": info_id},
                projection={'_id': 0}
            )
        except PyMongoError as err:
            LOGGER.error("Couldn't retrieve static info (%s): %s", info_id, err)
            return None

        return cursor.get("data", [])

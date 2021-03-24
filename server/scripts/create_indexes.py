"""This module provides creating indexes in mongo database."""

import logging

import pymongo

from app import MONGO_DATABASE


LOGGER = logging.getLogger(__name__)

STOPS_COORDINATES_INDEX_NAME = "stops_coordinates_index"


def create_index(collection, index_field, index_type, index_name):
    """Create index if not exists."""
    if index_name in collection.index_information():
        LOGGER.error(
            "Index `%s` (%s: %s) already exists in `%s` collection.",
            index_name, index_field, index_type, collection.name
        )
        return

    try:
        result = collection.create_index([(index_field, index_type)], name=index_name)
        if result:
            LOGGER.info("Index `%s` was successfully created.", index_name)
        else:
            LOGGER.error("Failed to create `%s` index.", index_name)
    except pymongo.errors.PyMongoError as err:
        LOGGER.error("Failed to create `%s` index: %s.", index_name, err)


def create_indexes():
    """
    Create indexes in collection if not exists:
        1. stops: 2d index on `coordinates`
    """
    create_index(
        collection=MONGO_DATABASE.stops,
        index_field="coordinates",
        index_type=pymongo.GEO2D,
        index_name=STOPS_COORDINATES_INDEX_NAME
    )


if __name__ == '__main__':
    create_indexes()

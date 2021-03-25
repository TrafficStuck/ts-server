"""This module provides creating indexes in mongo database."""

import logging

import pymongo

from app import MONGO_DATABASE


LOGGER = logging.getLogger(__name__)

STOPS_COORDINATES_INDEX_NAME = "stops_coordinates_index"
STOPS_NAMES_INDEX_NAME = "stops_names_index"
TRAFFIC_CONGESTION_REGION_INDEX_NAME = "traffic_congestion_region_index"
TRAFFIC_NAME_TIMESTAMP_INDEX_NAME = "traffic_name_timestamp_index"


def create_index(collection, index, index_name):
    """Create index if not exists."""
    if index_name in collection.index_information():
        LOGGER.error(
            "Index `%s` (%s) already exists in `%s` collection.",
            index_name, index, collection.name
        )
        return

    try:
        result = collection.create_index(index, name=index_name)
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
        2. stops: text index on `stop_name` and `stop_desc`
        3. traffic_congestion: text index on `region`
    """
    create_index(
        collection=MONGO_DATABASE.stops,
        index=[("coordinates", pymongo.GEO2D)],
        index_name=STOPS_COORDINATES_INDEX_NAME
    )
    create_index(
        collection=MONGO_DATABASE.stops,
        index=[("stop_name", pymongo.TEXT), ("stop_desc", pymongo.TEXT)],
        index_name=STOPS_NAMES_INDEX_NAME
    )
    create_index(
        collection=MONGO_DATABASE.traffic_congestion,
        index=[("region", pymongo.ASCENDING)],
        index_name=TRAFFIC_CONGESTION_REGION_INDEX_NAME
    )
    create_index(
        collection=MONGO_DATABASE.traffic,
        index=[("route_short_name", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)],
        index_name=TRAFFIC_NAME_TIMESTAMP_INDEX_NAME
    )


if __name__ == '__main__':
    create_indexes()

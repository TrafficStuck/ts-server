"""This modules provides functionality to work with traffic timeseries."""

import logging

import pymongo

from app import MONGO_DATABASE, REDIS
from app.helpers.outliers import iqr
from app.utils.time import get_time_range


LOGGER = logging.getLogger(__name__)


MIN_DISTANCE_CACHE_KEY = "MIN_DISTANCE"


class Congestion:
    """Class that provides method to work with traffic congestion."""

    collection = MONGO_DATABASE.traffic_congestion

    @classmethod
    def get_region_congestion(cls, region, limit):
        """Retrieve region congestion by region name."""
        try:
            result = cls.collection.find(
                filter={"id": region},
                limit=limit,
                projection={'_id': 0},
                sort=[("timestamp", pymongo.DESCENDING)]
            )
        except pymongo.errors.PyMongoError as err:
            LOGGER.error("Couldn't retrieve region congestion (%s): %s", region, err)
            return None

        return list(result)


class Traffic:
    """Class that provides methods for interaction with traffic timeseries."""

    collection = MONGO_DATABASE.traffic

    @staticmethod
    def _format_timeseries(cursor):
        """Return format timeseries - timestamp:value."""
        return [
            {"timestamp": x["_id"]["timestamp"], "value": x["value"]} for x in cursor
        ]

    @classmethod
    def get_route_avg_speed(cls, route, delta):
        """Retrieve aggregated timeseries by route average speed."""
        start, end = get_time_range(delta)
        pipeline = [
            {"$match": {
                "route_short_name": route,
                "timestamp": {"$gte": start, "$lte": end}
            }},
            {"$group": {
                "_id": {
                    "route_short_name": "$route_short_name",
                    "timestamp": "$timestamp"
                },
                "value": {"$avg": "$trip_speed"}
            }},
            {"$sort": {"_id.timestamp": 1}}
        ]
        try:
            cursor = cls.collection.aggregate(pipeline)
        except pymongo.errors.PyMongoError as err:
            LOGGER.error("Couldn't retrieve aggregated timeseries: %s", err)
            return None

        return cls._format_timeseries(cursor)

    @classmethod
    def get_route_trips_count(cls, route, delta):
        """Retrieve aggregated timeseries by routes trips count."""
        start, end = get_time_range(delta)
        pipeline = [
            {"$match": {
                "route_short_name": route,
                "timestamp": {"$gte": start, "$lte": end}
            }},
            {"$group": {
                "_id": {
                    "route_short_name": "$route_short_name",
                    "timestamp": "$timestamp"
                },
                "value": {"$sum": 1}
            }},
            {"$sort": {"_id.timestamp": 1}}
        ]
        try:
            cursor = cls.collection.aggregate(pipeline)
        except pymongo.errors.PyMongoError as err:
            LOGGER.error("Couldn't retrieve aggregated timeseries: %s", err)
            return None

        return cls._format_timeseries(cursor)

    @classmethod
    def get_route_avg_distance(cls, route, delta):
        """Retrieve aggregated timeseries by routes trip distance."""
        start, end = get_time_range(delta)
        pipeline = [
            {"$match": {
                "route_short_name": route,
                "timestamp": {"$gte": start, "$lte": end}
            }},
            {"$group": {
                "_id": {
                    "route_short_name": "$route_short_name",
                    "timestamp": "$timestamp"
                },
                "value": {"$avg": "$trip_distance"}
            }},
            {"$sort": {"_id.timestamp": 1}}
        ]
        try:
            cursor = cls.collection.aggregate(pipeline)
        except pymongo.errors.PyMongoError as err:
            LOGGER.error("Couldn't retrieve aggregated timeseries: %s", err)
            return None

        return cls._format_timeseries(cursor)

    @classmethod
    def get_routes_distances(cls, delta):
        """Return all routes distances for the provided period."""
        start, end = get_time_range(delta)
        try:
            cursor = cls.collection.find(
                filter={
                    "trip_distance": {"$ne": 0},
                    "timestamp": {"$gte": start, "$lte": end}
                },
                projection={"_id": 0, "trip_distance": 1}
            )
        except pymongo.errors.PyMongoError as err:
            LOGGER.error("Couldn't retrieve routes distances: %s", err)
            return None

        return list(cursor)

    @classmethod
    def get_routes_min_distance(cls, delta):
        """Return min routes distances for the provided period."""
        min_distance = REDIS.get(MIN_DISTANCE_CACHE_KEY)
        if not min_distance:
            routes_distances = cls.get_routes_distances(delta)
            routes_distances = iqr([x["trip_distance"] for x in routes_distances], q1_bound=0.1)
            if routes_distances:
                min_distance = min(routes_distances)
                REDIS.set(MIN_DISTANCE_CACHE_KEY, min_distance, 1)  # TODO: set cache

        return min_distance

    @classmethod
    def get_route_coordinates(cls, route):
        """Retrieve coordinates for route."""
        pipeline = [
            {"$match": {"route_short_name": route}},
            {"$group": {
                "_id": {
                    "route_name": "$route_short_name",
                    "timestamp": "$timestamp"
                },
                "value": {
                    "$addToSet": {
                        "latitude": "$trip_latitude",
                        "longitude": "$trip_longitude"
                    }
                }
            }},
            {"$sort": {"_id.timestamp": -1}},
            {"$limit": 1}
        ]
        try:
            cursor = cls.collection.aggregate(pipeline)
        except pymongo.errors.PyMongoError as err:
            LOGGER.error("Couldn't retrieve aggregated timeseries: %s", err)
            return None

        return cls._format_timeseries(cursor)

    @classmethod
    def get_routes_names(cls, delta):
        """Retrieve unique route names for the specific period."""
        start, end = get_time_range(delta)
        pipeline = [
            {"$match": {
                "route_short_name": {"$ne": ""},
                "timestamp": {"$gte": start, "$lte": end},
            }},
            {"$group": {
                "_id": "$route_type",
                "route_names": {"$addToSet": "$route_short_name"}
            }}
        ]
        try:
            cursor = cls.collection.aggregate(pipeline)
        except pymongo.errors.PyMongoError as err:
            LOGGER.error("Couldn't retrieve aggregated timeseries: %s", err)
            return None

        return cursor

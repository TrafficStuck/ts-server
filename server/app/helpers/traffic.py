"""This modules provides functionality to work with traffic timeseries."""

import logging

from pymongo.errors import PyMongoError

from app import MONGO_DATABASE
from app.utils.misc import get_time_range


LOGGER = logging.getLogger(__name__)


class Congestion:
    """Class that provides method to work with traffic congestion."""

    collection = MONGO_DATABASE.traffic_congestion

    @classmethod
    def get_region_congestion(cls, region, limit):
        """Retrieve region congestion by region name."""
        try:
            result = list(cls.collection.find(
                filter={"id": region},
                limit=limit,
                projection={'_id': 0}
            ))
        except (PyMongoError, TypeError) as err:
            LOGGER.error("Couldn't retrieve region congestion (%s): %s", region, err)
            return None

        return result


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
        except PyMongoError as err:
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
        except PyMongoError as err:
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
        except PyMongoError as err:
            LOGGER.error("Couldn't retrieve aggregated timeseries: %s", err)
            return None

        return cls._format_timeseries(cursor)

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
        except PyMongoError as err:
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
        except PyMongoError as err:
            LOGGER.error("Couldn't retrieve aggregated timeseries: %s", err)
            return None

        return cursor

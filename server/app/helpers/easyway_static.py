"""This module provides helper functionality to work with easyway data."""

import re
import collections

from shapely.geometry import Polygon

from app import APP_CONFIG
from app.utils.misc import load_csv, load_json


ROUTE_TYPE_MAP = {
    "А": "Автобус",
    "Н-А": "Нічний Автобус",
    "Т": "Трамвай",
    "Тр": "Тролейбус"
}

STATIC_ROUTES_FILE = f"{APP_CONFIG.STATIC_DIR}/routes.txt"
STATIC_AGENCY_FILE = f"{APP_CONFIG.STATIC_DIR}/agency.txt"
STATIC_TRIPS_FILE = f"{APP_CONFIG.STATIC_DIR}/trips.txt"
STATIC_REGIONS_FILE = f"{APP_CONFIG.STATIC_DIR}/regions.json"
STATIC_STOP_TIMES_FILE = f"{APP_CONFIG.STATIC_DIR}/stop_times.txt"
STATIC_STOPS_FILE = f"{APP_CONFIG.STATIC_DIR}/stops.txt"


def get_routes_names():
    """Return short name for each route id."""
    routes_csv = load_csv(STATIC_ROUTES_FILE)

    return {route["route_id"]: route["route_short_name"] for route in routes_csv}


def get_routes():
    """Load csv file with static data for routes in Lviv."""
    agency_csv = load_csv(STATIC_AGENCY_FILE)
    routes_csv = load_csv(STATIC_ROUTES_FILE)

    agencies = {agency["agency_id"]: agency["agency_name"] for agency in agency_csv}
    routes = []
    for route in routes_csv:
        route_short_name = route["route_short_name"]
        route_type_short = re.sub(r"\d+", "", route_short_name)
        route_type = ROUTE_TYPE_MAP.get(route_type_short, "Інші")

        routes.append({
            "id": route["route_id"],
            "route_type": route_type,
            "short_name": route_short_name,
            "long_name": route["route_long_name"],
            "agency_id": route["agency_id"],
            "agency_name": agencies[route["agency_id"]],
            "trips": [],
        })

    return routes


def get_routes_trips():
    """Return list of trips for each route in Lviv."""
    trips_csv = load_csv(STATIC_TRIPS_FILE)

    routes_trips = collections.defaultdict(set)
    for trip in trips_csv:
        route_id = trip["route_id"]
        trip_id = trip["block_id"]
        routes_trips[route_id].add(trip_id)

    return routes_trips


def get_trips():
    """Return trip_id and route_id mapping"""
    trips_csv = load_csv(STATIC_TRIPS_FILE)

    trips = {}
    for trip in trips_csv:
        trip_id = trip["trip_id"]
        route_id = trip["route_id"]

        trips[trip_id] = route_id

    return trips


def get_stops():
    """Return stops information from static stops file."""
    stops_csv = load_csv(STATIC_STOPS_FILE)

    stops = {}
    for stop in stops_csv:
        stop_id = stop["stop_id"]
        stop_latitude = float(stop["stop_lat"])
        stop_longitude = float(stop["stop_lon"])
        stop_name = stop["stop_name"]
        stop_desc = stop["stop_desc"]

        stops[stop_id] = {
            "stop_name": stop_name,
            "stop_desc": stop_desc,
            "coordinates": [stop_latitude, stop_longitude]
        }

    return stops


def get_regions_bounds():
    """Return polygon for each region by its bounds."""
    regions_bounds = load_json(STATIC_REGIONS_FILE)
    regions_polygons = {k: Polygon(v) for k, v in regions_bounds.items()}

    return regions_polygons

"""This module provides helper functionality to work with easyway data."""

import re
import collections
from datetime import datetime

from google import protobuf
from google.transit import gtfs_realtime_pb2
from shapely.geometry import Point

from app.utils.misc import load_csv
from app.utils.time import get_time_integer
from app.helpers.traffic import Traffic
from app.helpers.easyway_static import (
    STATIC_STOP_TIMES_FILE,
    get_routes_names,
    get_regions_bounds,
    get_routes_trips,
    get_routes,
    get_trips,
    get_stops
)


ROUTE_TYPE_MAP = {
    "А": "Автобус",
    "Н-А": "Нічний Автобус",
    "Т": "Трамвай",
    "Тр": "Тролейбус"
}


def parse_traffic(gtfs, timestamp, prev_odometers):
    """Compile and parse GTFS data using protobuf to dictionary format."""
    feed = gtfs_realtime_pb2.FeedMessage()

    try:
        feed.ParseFromString(gtfs)
    except protobuf.message.DecodeError:
        return None

    traffic = []
    route_type_re = re.compile(r"\d+")
    route_names = get_routes_names()
    for entity in feed.entity:
        vehicle = entity.vehicle
        position = vehicle.position
        route_id = vehicle.trip.route_id
        license_plate = vehicle.vehicle.license_plate.replace("-", "")

        route_short_name = route_names.get(route_id, "")
        route_type_short = re.sub(route_type_re, "", route_short_name)
        route_type = ROUTE_TYPE_MAP.get(route_type_short, "Інші")
        prev_odometer = prev_odometers.get(vehicle.vehicle.id, position.odometer)

        traffic.append({
            "route_id": route_id,
            "route_short_name": route_short_name,
            "route_type": route_type,

            "trip_latitude": position.latitude,
            "trip_longitude": position.longitude,
            "trip_vehicle_id": vehicle.vehicle.id,
            "trip_license_plate": license_plate,
            "trip_bearing": position.bearing,
            "trip_speed": position.speed * 3.6,
            "trip_odometer": position.odometer,
            "trip_distance": position.odometer - prev_odometer,

            "timestamp": timestamp,
            "date": datetime.now().isoformat()
        })

    return traffic


def parse_traffic_congestion(traffic, timestamp):
    """Return parsed traffic congestion by regions."""
    regions_speeds = collections.defaultdict(list)
    regions_polygons = get_regions_bounds()
    for route in traffic:
        trip_speed = route["trip_speed"]
        point = Point((route["trip_latitude"], route["trip_longitude"]))
        for name, poly in regions_polygons.items():
            if poly.contains(point):
                regions_speeds[name].append(trip_speed)

    traffic_congestions = []
    min_speed = Traffic.get_routes_min_speed()
    for region, region_speeds in regions_speeds.items():
        region_speeds = list(filter(lambda x: x != 0, region_speeds))
        try:
            region_avg_speed = sum(region_speeds) / len(region_speeds)
            region_congestion = (100 * min_speed) / region_avg_speed
        except (ZeroDivisionError, TypeError):
            continue
        else:
            traffic_congestions.append({
                "id": region,
                "value": region_congestion,
                "timestamp": timestamp
            })

    return traffic_congestions


def get_stops_per_routes():
    """Return dict with data about count of stops per routes."""
    routes_trips = get_routes_trips()
    routes_names = get_routes_names()

    trips_map = {}
    for route, trips in routes_trips.items():
        trips_map.update({trip: route for trip in trips})

    stops = set()
    stop_times = load_csv(STATIC_STOP_TIMES_FILE)
    for stop_time in stop_times:
        trip_id = stop_time["trip_id"].split("_")[0]
        stop_id = stop_time["stop_id"]
        route_id = trips_map[trip_id]
        route_name = routes_names[route_id]
        stops.add((route_name, stop_id))

    routes = dict.fromkeys(routes_names.values(), 0)
    for route_name, stop_id in stops:
        routes[route_name] += 1

    stops_count = [{"id": k, "value": v} for k, v in routes.items()]
    return stops_count


def get_transport_counts():
    """Return transport counts per agency, transport type and certain route."""
    routes = get_routes()
    routes_trips = get_routes_trips()

    agencies_counter = collections.Counter([route["agency_name"] for route in routes])
    agencies_count = [{"id": k, "value": v} for k, v in agencies_counter.items()]

    routes_per_type = [route["route_type"] for route in routes]
    route_type_counter = collections.Counter(routes_per_type)
    route_type_count = [{"id": k, "value": v} for k, v in route_type_counter.items()]

    route_names = {route["id"]: route["short_name"] for route in routes}
    routes_count = [
        {"id": route_names[route_id], "value": len(set(trips_ids))}
        for route_id, trips_ids in routes_trips.items()
    ]

    return {
        "transport_per_agencies": agencies_count,
        "transport_per_type": route_type_count,
        "transport_per_routes": routes_count,
    }


def get_stops_data():
    """Return full stop times information."""
    stops = get_stops()
    trips = get_trips()
    routes_names = get_routes_names()

    stops_times_csv = load_csv(STATIC_STOP_TIMES_FILE)
    for stop_time in stops_times_csv:
        stop_id = stop_time["stop_id"]
        stop = stops[stop_id]
        if "arrivals" not in stop:
            stop["arrivals"] = []

        trip_id = stop_time["trip_id"]
        route_id = trips[trip_id]
        route_name = routes_names[route_id]
        arrival_time = stop_time["arrival_time"]

        stop["arrivals"].append({
            "route_name": route_name,
            "arrival_time": arrival_time,
            "arrival_time_integer": get_time_integer(arrival_time)
        })

    return stops

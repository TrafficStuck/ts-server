"""This module provides API views for timeseries data."""

from urllib import parse

from flask import Blueprint, request

from app import CACHE
from app.utils.misc import response
from app.helpers.traffic import Traffic, Congestion


traffic_blueprint = Blueprint('traffic-stuck', __name__)


@traffic_blueprint.route("traffic/<route>/avg_speed", methods=["GET"])
@CACHE.cached()
def get_route_avg_speed(route):
    """Return aggregated routes timeseries by avg speed."""
    route = parse.unquote(route, encoding="utf-8")
    delta = request.args.get("delta", type=float, default=3600)
    timeseries = Traffic.get_route_avg_speed(route, delta)
    if timeseries is None:
        message = "Couldn't retrieve data from database. Try again, please."
        return response(False, message, 503)

    return response(True, timeseries, 200)


@traffic_blueprint.route("traffic/<route>/trips_count", methods=["GET"])
@CACHE.cached()
def get_route_trips_count(route):
    """Return aggregated routes timeseries by trips count."""
    route = parse.unquote(route, encoding="utf-8")
    delta = request.args.get("delta", type=float, default=3600)
    timeseries = Traffic.get_route_trips_count(route, delta)
    if timeseries is None:
        message = "Couldn't retrieve data from database. Try again, please."
        return response(False, message, 503)

    return response(True, timeseries, 200)


@traffic_blueprint.route("traffic/<route>/avg_distance", methods=["GET"])
@CACHE.cached()
def get_route_avg_distance(route):
    """Return aggregated routes timeseries by avg_distance."""
    route = parse.unquote(route, encoding="utf-8")
    delta = request.args.get("delta", type=float, default=3600)
    timeseries = Traffic.get_route_avg_distance(route, delta)
    if timeseries is None:
        message = "Couldn't retrieve data from database. Try again, please."
        return response(False, message, 503)

    return response(True, timeseries, 200)


@traffic_blueprint.route("traffic/<route>/coordinates", methods=["GET"])
@CACHE.cached()
def get_route_coordinates(route):
    """Return route coordinates for the last collected time."""
    route = parse.unquote(route, encoding="utf-8")
    timeseries = Traffic.get_route_coordinates(route)
    if timeseries is None:
        message = "Couldn't retrieve data from database. Try again, please."
        return response(False, message, 503)

    coordinates = timeseries[0] if timeseries else None
    return response(True, coordinates, 200)


@traffic_blueprint.route("traffic/routes", methods=['GET'])
@CACHE.cached()
def get_routes_names():
    """Return json response with available routes from easyway for last period."""
    delta = request.args.get("delta", type=float, default=3600)
    result = Traffic.get_routes_names(delta)
    if result is None:
        message = "Couldn't retrieve data from database. Try again, please."
        return response(False, message, 503)

    routes = []
    for route in result:
        route_names = sorted(route["route_names"])
        routes.append({"route_type": route["_id"], "route_names": route_names})

    routes = sorted(routes, key=lambda x: -len(x["route_names"]))
    return response(True, routes, 200)


@traffic_blueprint.route("traffic/congestion/<region>", methods=['GET'])
@CACHE.cached()
def get_regions_congestion(region):
    """Return city region traffic congestion."""
    region = parse.unquote(region, encoding="utf-8")
    limit = request.args.get("limit", type=int, default=15)
    result = Congestion.get_region_congestion(region, limit)
    if result is None:
        message = "Couldn't retrieve data from database. Try again, please."
        return response(False, message, 503)

    return response(True, result, 200)

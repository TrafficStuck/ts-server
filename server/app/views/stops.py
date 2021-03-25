"""This module provides API views for timeseries data."""

from http import HTTPStatus
from datetime import datetime

from flask import Blueprint, request

from app.utils.time import TIME_FORMAT, get_time_integer
from app.utils.misc import make_response
from app.helpers.stops import Stops


stops_blueprint = Blueprint('traffic-stuck-stops', __name__)


@stops_blueprint.route("stops/nearest", methods=["GET"])
def get_nearest_stops():
    """Return the nearest stops by provided latitude and longitude."""
    limit = request.args.get("limit", type=int, default=5)
    latitude = request.args.get("latitude", type=float)
    longitude = request.args.get("longitude", type=float)
    if not latitude or not longitude:
        message = "The required params latitude and longitude weren't provided."
        return make_response(False, message, HTTPStatus.BAD_REQUEST)

    nearest_stops = Stops.get_nearest_stops(latitude, longitude, limit)
    if nearest_stops is None:
        message = "Couldn't retrieve data from database. Try again, please."
        return make_response(False, message, HTTPStatus.BAD_REQUEST)

    return make_response(True, nearest_stops, HTTPStatus.OK)


@stops_blueprint.route("stops/<stop_id>/arrivals", methods=["GET"])
def get_nearest_arrivals(stop_id):
    """Return the nearest arrivals for provided stop id."""
    stop = Stops.get_stop_by_id(stop_id)
    if stop is None:
        message = "Couldn't retrieve data from database. Try again, please."
        return make_response(False, message, HTTPStatus.BAD_REQUEST)

    time_start = get_time_integer(datetime.now().strftime(TIME_FORMAT))
    time_end = time_start + 3600
    nearest_arrivals = filter(lambda x: time_start <= x["arrival_time_integer"] <= time_end, stop["arrivals"])

    return make_response(True, list(nearest_arrivals), HTTPStatus.OK)

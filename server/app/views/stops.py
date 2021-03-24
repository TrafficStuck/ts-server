"""This module provides API views for timeseries data."""

from flask import Blueprint, request

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
        return make_response(False, message, 400)

    nearest_stops = Stops.get_nearest_stops(latitude, longitude, limit)
    if nearest_stops is None:
        message = "Couldn't retrieve data from database. Try again, please."
        return make_response(False, message, 503)

    return make_response(True, nearest_stops, 200)

"""This module provides API views for static data."""

from http import HTTPStatus

from flask import Blueprint

from app import CACHE
from app.utils.misc import make_response
from app.helpers.static import Static


static_blueprint = Blueprint('traffic-stuck-static', __name__)


@static_blueprint.route("static/<info_id>", methods=['GET'])
@CACHE.cached(timeout=86400)  # 1 day in seconds
def get_routes_static_info(info_id):
    """Return routes static information by id."""
    result = Static.get_static_info(info_id)
    if result is None:
        message = "Couldn't retrieve data from database. Try again, please."
        return make_response(False, message, HTTPStatus.BAD_REQUEST)

    info = sorted(result, key=lambda x: -x["value"])
    return make_response(True, info, HTTPStatus.OK)

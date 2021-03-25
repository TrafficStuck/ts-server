"""This module provides basic server endpoints."""

from http import HTTPStatus

from flask import Blueprint, request

from app.utils.misc import make_response


internal_blueprint = Blueprint('traffic-stuck-internal', __name__)


@internal_blueprint.route("/health", methods=['GET'])
def get_health():
    """Return health OK http status."""
    return make_response(True, "OK", HTTPStatus.OK)


def handle_404(error):
    """Return custom response for 404 http status code."""
    return make_response(
        False,
        f"The endpoint ({request.path}) you are trying to access could not be found on the server.",
        error.code
    )


def handle_405(error):
    """Return custom response for 405 http status code."""
    return make_response(
        False,
        f"The method ({request.method}) you are trying to use for this URL could not be handled on the server.",
        error.code
    )


def handle_500(error):
    """Return custom response for 500 http status code."""
    return make_response(
        False,
        "Something has gone wrong on the server side. Please, try again later.",
        error.code
    )

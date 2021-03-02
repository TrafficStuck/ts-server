"""This module provides helper functionality for collector application."""

from datetime import datetime

from flask import jsonify


def get_time_range(delta):
    """Return time range by delta."""
    end = datetime.now().timestamp()
    start = end - delta
    return start, end


def response(success, result, status_code):
    """Return prepared http json response."""
    json_result = jsonify({"success": success, "result": result})
    return json_result, status_code

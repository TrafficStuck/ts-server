"""This module provides helper functionality for collector application."""

from datetime import datetime


TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


def get_time_range(delta):
    """Return time range by delta."""
    end = datetime.now().timestamp()
    start = end - delta
    return start, end


def get_time_integer(time):
    """Return time as integer value."""
    hours, minutes, seconds = time.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

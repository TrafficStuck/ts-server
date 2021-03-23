"""This module provides celery tasks."""

import logging
import pickle

from pymongo.errors import PyMongoError
from celery.signals import worker_ready

from app import MONGO_DATABASE, CELERY_APP, REDIS, APP_CONFIG
from app.utils.misc import download_context, unzip
from app.utils.easyway import (
    get_transport_counts,
    get_stops_per_routes,
    get_stops_data,
    parse_traffic,
    parse_traffic_congestion,
)


LOG = logging.getLogger(__name__)

TRAFFIC_COLLECTION = MONGO_DATABASE.traffic
TRAFFIC_CONGESTION_COLLECTION = MONGO_DATABASE.traffic_congestion

STATIC_URL = "http://track.ua-gis.com/gtfs/lviv/static.zip"
VEHICLE_URL = "http://track.ua-gis.com/gtfs/lviv/vehicle_position"
GTFS_ODOMETERS_KEY = "GTFS_ODOMETERS"
STATIC_FILE = f"{APP_CONFIG.STATIC_DIR}/static.zip"


@worker_ready.connect
def at_start(sender, **kwargs):
    """Run following tasks on the celery work startup."""
    with sender.app.connection() as conn:
        sender.app.send_task("app.tasks.prepare_easyway_static", connection=conn)


@CELERY_APP.task(
    bind=True,
    default_retry_delay=30,  # 30 seconds for retry delay
    retry_kwargs={"max_retries": 5})  # 5 maximum retry attempts
def collect_traffic(self):
    """
    Defines commands to download data about Lviv transport geolocation,
    compile it to the dictionary format and insert it to the database.
    """
    gtfs_content = download_context(VEHICLE_URL)
    if not gtfs_content:
        LOG.error("Failed to download file with GTFS data.")
        raise self.retry()

    try:
        prev_odometers = pickle.loads(REDIS.get(GTFS_ODOMETERS_KEY))
    except (TypeError, pickle.UnpicklingError):
        prev_odometers = {}

    traffic = parse_traffic(gtfs_content, prev_odometers)
    if not traffic:
        LOG.error("Failed to compile GTFS data to json format.")
        raise self.retry()

    traffic_congestion = parse_traffic_congestion(traffic)
    try:
        TRAFFIC_COLLECTION.insert_many(traffic)
        TRAFFIC_CONGESTION_COLLECTION.insert_many(traffic_congestion)
    except PyMongoError as err:
        LOG.error("Failed to insert collected routes: %s", err)
        raise self.retry()

    # TODO: think about prev odometers
    traffic_odometers = {x["trip_vehicle_id"]: x["trip_odometer"] for x in traffic}
    REDIS.set(GTFS_ODOMETERS_KEY, pickle.dumps(traffic_odometers))

    LOG.info("Successfully collected %s trips.", len(traffic))


@CELERY_APP.task(
    bind=True,
    default_retry_delay=30,  # 30 seconds for retry delay
    retry_kwargs={"max_retries": 2})
def prepare_easyway_static(self):
    """
    Download and unzip static files from easy way.
    Calculate count transports per agency, transport type
    and certain route, count transport stops routes.
    Save calculated data to `transport` collection.
    """
    downloaded = download_context(STATIC_URL, STATIC_FILE)
    if not downloaded:
        LOG.warning("Failed to download easyway static data.")
        raise self.retry()

    unzipped = unzip(STATIC_FILE, APP_CONFIG.STATIC_DIR)
    if not unzipped:
        LOG.warning("Failed to unzip easyway static data.")
        raise self.retry()

    transport_counts = get_transport_counts()
    stops_per_routes = get_stops_per_routes()
    easyway_static_data = {
        "stops_per_routes": stops_per_routes,
        **transport_counts
    }

    docs = [{"id": k, "data": v} for k, v in easyway_static_data.items()]
    try:
        # TODO: transaction
        MONGO_DATABASE.transport.drop()
        MONGO_DATABASE.transport.insert_many(docs)
    except PyMongoError as err:
        LOG.error("Failed to insert routes easyway static data: %s", err)
        raise self.retry()

    prepare_stops_times.delay()
    LOG.info("Successfully inserted easyway static data.")


@CELERY_APP.task(
    bind=True,
    default_retry_delay=30,  # 30 seconds for retry delay
    retry_kwargs={"max_retries": 2})
def prepare_stops_times(self):
    """
    Parse a couple static files (trips, routes, stops, stop_times) in order
    to format full stop times information and insert it into stops collection.
    """
    stops_times = get_stops_data()
    docs = [{"id": k, **v} for k, v in stops_times.items()]
    try:
        # TODO: transaction
        MONGO_DATABASE.stops.drop()
        MONGO_DATABASE.stops.insert_many(docs)
    except PyMongoError as err:
        LOG.error("Failed to insert stops easyway static data: %s", err)
        raise self.retry()

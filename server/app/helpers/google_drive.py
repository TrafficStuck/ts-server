"""The module that provides functionality to work with google drive."""

import logging

from googleapiclient import discovery, http, errors
from google.oauth2.service_account import Credentials

from app import APP_CONFIG


LOGGER = logging.getLogger(__name__)


class GoogleDrive:
    """Class that provides functionality to work with google drive"""

    GOOGLE_DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
    GOOGLE_DRIVE_SERVICE = "drive"
    GOOGLE_DRIVE_SERVICE_VERSION = "v3"

    @classmethod
    def get_credentials(cls):
        """Return google oauth2 credentials object."""
        return Credentials.from_service_account_file(
            APP_CONFIG.GOOGLE_CREDENTIALS_FILE,
            scopes=[cls.GOOGLE_DRIVE_SCOPE]
        )

    @classmethod
    def upload_file(cls, name, directory_id, data, mimetype):
        """Upload file data to provided google drive directory."""
        file_metadata = {
            "name": name,
            "parents": [directory_id],
            "mimeType": mimetype
        }

        try:
            credentials = cls.get_credentials()
        except FileNotFoundError:
            LOGGER.error("Failed to load credentials from file: %s", APP_CONFIG.GOOGLE_CREDENTIALS_FILE)
            return None

        try:
            google_drive = discovery.build(
                cls.GOOGLE_DRIVE_SERVICE,
                cls.GOOGLE_DRIVE_SERVICE_VERSION,
                credentials=credentials
            )
            file_media = http.MediaIoBaseUpload(data, mimetype=mimetype, resumable=True)
            file_id = google_drive.files().create(body=file_metadata, media_body=file_media, fields="id").execute()
        except errors.Error as err:
            LOGGER.error("Failed to upload file into google drive: %s", err)
            return None

        return file_id["id"]

import os
from enum import Enum

UNCLASSIFIED_SONG_KEY_NAME = "unclassified"


class ExportDestination(Enum):
    SPOTIFY = "spotify"

    @property
    def export(self):
        from export.spotify import SpotifyExportClient

        __export_callable_mapping = {
            self.SPOTIFY: SpotifyExportClient().export,
        }
        return __export_callable_mapping[self]


class TelegramConfig:
    TELEGRAM_API_ID: int = int(os.getenv("TELEGRAM_API_ID"))
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_APP_TITLE: str = os.getenv("TELEGRAM_APP_TITLE")
    TELEGRAM_SHORT_NAME: str = os.getenv("TELEGRAM_SHORT_NAME")


class SpotifyConfig:
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

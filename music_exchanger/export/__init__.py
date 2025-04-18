from enum import Enum


class ExportDestination(Enum):
    SPOTIFY = "spotify"

    @property
    def export(self):
        from spotify import SpotifyExportClient

        __export_callable_mapping = {
            self.SPOTIFY: SpotifyExportClient().export,
        }
        return __export_callable_mapping[self]

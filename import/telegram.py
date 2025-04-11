import time
from collections import defaultdict

from singleton.singleton import Singleton
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterMusic

from settings import TelegramConfig, ExportDestination, UNCLASSIFIED_SONG_KEY_NAME


class TelegramExport:
    def export(self, destination: ExportDestination):
        destination.export(self._export_data)


class ResponseDataStatistics:
    def most_sings_per_performer(self):
        pass

    @property
    def found_data(self):
        return self._export_data

    @property
    def num_unique_songs(self):
        return sum(len(s) for s in self._export_data.values())


class TelegramQueryResponse(TelegramExport, ResponseDataStatistics):
    def __init__(
        self,
        num_songs_found,
        response_data,
        query_execution_time,
        query_limit,
    ):
        self._export_data = response_data
        self.query_count = num_songs_found
        self.query_execution_time = query_execution_time
        self.query_limit = query_limit

    def add_to_global_export(self):
        TelegramMusicExportClient.instance().expand_global_export(self._export_data)


@Singleton
class TelegramMusicExportClient(TelegramClient, TelegramExport, ResponseDataStatistics):
    def __init__(self, **kwargs):
        self._export_data = defaultdict(set)

        super().__init__(
            session="test_session",
            api_id=TelegramConfig.TELEGRAM_API_ID,
            api_hash=TelegramConfig.TELEGRAM_API_HASH,
            **kwargs,
        )

    def get_songs_data_from_target(
        self,
        target: str,
        limit: int = 3000,
        add_to_global_export: bool = False,
    ) -> TelegramQueryResponse:

        num_songs_found = 0
        response_data = defaultdict(set)

        start = time.time()

        for msg in self.iter_messages(
            entity=target,
            filter=InputMessagesFilterMusic,
            limit=limit,
        ):
            num_songs_found += 1
            name = msg.file.name.rsplit(".", 1)[0]

            if performer := msg.file.performer:
                response_data[performer].add(name)
            else:
                response_data[UNCLASSIFIED_SONG_KEY_NAME].add(name)

        end = time.time()

        if add_to_global_export:
            self.expand_global_export(response_data)

        return TelegramQueryResponse(
            num_songs_found,
            response_data,
            query_execution_time=end - start,
            query_limit=limit,
        )

    def expand_global_export(self, new_data: dict[str, set]):
        for key in new_data.keys():
            self._export_data[key].update(new_data[key])

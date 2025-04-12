import time
from collections import defaultdict

from telethon.errors import (
    SessionPasswordNeededError,
    PasswordHashInvalidError,
)
from .exceptions import UnauthorizedError
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterMusic

from singleton.singleton import Singleton

from .utils import display_url_as_qr
from settings import TelegramConfig, UNCLASSIFIED_SONG_KEY_NAME
from .mixins import TelegramExportMixin, ResponseDataStatsMixin


class TelegramQueryResponse(
    TelegramExportMixin,
    ResponseDataStatsMixin,
):
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


class TelegramAuthClient(TelegramClient):
    def start(self, *args, **kwargs):
        if not self.loop.run_until_complete(self.is_user_authorized()):
            raise UnauthorizedError(
                "Telegram client is not authorized. Please use auth first."
            )

        super().start(*args, **kwargs)

    def auth(self, qr_login: bool = False):
        if qr_login:
            self.loop.run_until_complete(self._login_with_qr())
        self.start()

    async def _login_with_qr(self):
        qr_login = await self.qr_login()
        print("Is connected:", self.is_connected())

        authorized = False
        while not authorized:
            display_url_as_qr(qr_login.url)

            try:
                authorized = await qr_login.wait(10)
            except TimeoutError:
                await qr_login.recreate()
            except SessionPasswordNeededError:
                try:
                    await self.sign_in(password=str(input("Password: ")))
                    authorized = True
                except PasswordHashInvalidError:
                    print("Incorrect password")
                    break


@Singleton
class TelegramMusicExportClient(
    TelegramAuthClient,
    TelegramExportMixin,
    ResponseDataStatsMixin,
):
    def __init__(
        self,
        session: str = None,
        **kwargs,
    ):
        self._export_data = defaultdict(set)

        super().__init__(
            session=StringSession() if not session else session,
            api_id=TelegramConfig.TELEGRAM_API_ID,
            api_hash=TelegramConfig.TELEGRAM_API_HASH,
            **kwargs,
        )

        if not self.is_connected():
            self.loop.run_until_complete(self.connect())

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

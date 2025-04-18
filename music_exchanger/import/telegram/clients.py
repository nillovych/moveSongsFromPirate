import asyncio
import os
import time
from collections import defaultdict

from telethon.errors import (
    SessionPasswordNeededError,
    PasswordHashInvalidError,
)
from .exceptions import (
    Bad2FAPasswordGiven,
    UnauthenticatedTelegramClientException,
)
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterMusic

from singleton.singleton import Singleton

from .utils import display_url_as_qr
from music_exchanger.settings import UNCLASSIFIED_SONG_KEY_NAME
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


class LoginWithQRResult:
    def __init__(self):
        self.qr_image = None
        self.done = None
        self._update_qr_cb = None

    def set_qr_update_callback(self, func):
        self._update_qr_cb = func

    def update_qr(self, url):
        self.qr_image = display_url_as_qr(url)
        if self._update_qr_cb:
            self._update_qr_cb(self.qr_image)


class TelegramAuthClient(TelegramClient):
    def login_with_qr(
        self,
        pass_2fa: str = None,
    ):
        return self.loop.run_until_complete(self._login_with_qr_async(pass_2fa))

    async def _login_with_qr_async(
        self,
        pass_2fa: str = None,
        **kwargs,
    ):
        result = LoginWithQRResult()
        qr_login = await self.qr_login(**kwargs)
        result.update_qr(qr_login.url)

        async def wait():
            authorized = False
            while not authorized:
                try:
                    authorized = await qr_login.wait(timeout=5)
                except TimeoutError:
                    await qr_login.recreate()
                    result.update_qr(qr_login.url)

                # if 2FA exists for user
                except SessionPasswordNeededError:
                    try:
                        await self.sign_in(password=pass_2fa, **kwargs)
                        authorized = True
                    except PasswordHashInvalidError as e:
                        raise Bad2FAPasswordGiven() from e

            return True

        result.done = asyncio.ensure_future(wait(), loop=self.loop)
        return result


@Singleton
class TelegramMusicExportClient(
    TelegramAuthClient,
    TelegramExportMixin,
    ResponseDataStatsMixin,
):
    def __init__(
        self,
        session: str = None,
        api_id: str = None,
        api_hash: str = None,
        **kwargs,
    ):
        self._export_data = defaultdict(set)

        api_id: int = api_id or int(os.getenv("TELEGRAM_API_ID", None))
        api_hash: str = api_hash or os.getenv("TELEGRAM_API_HASH", None)

        if not api_id or not api_hash:
            raise UnauthenticatedTelegramClientException()

        super().__init__(
            session=StringSession() if not session else session,
            api_id=api_id,
            api_hash=api_hash,
            **kwargs,
        )

        if not self.is_connected():
            self.loop.run_until_complete(self.connect())

    def get_songs_data_from_target(
        self,
        target: str,
        limit: int = 3000,  # optimal
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

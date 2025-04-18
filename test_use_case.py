import os

from export import ExportDestination
from importTelegram.clients import TelegramMusicExportClient, TelegramQueryResponse

if __name__ == "__main__":
    # Initialize a singleton TelegramMusicExportClient with session specified,
    # if the corresponding session exists, or is planned to be saved after the auth
    TelegramMusicExportClient.initialize(session="test_session")

    # Instantiate client;
    # if you don't plan to save or reuse session – this is your first step
    client = TelegramMusicExportClient.instance()

    # Result object to be able to use QR Image in different ways
    result = client.login_with_qr(
        pass_2fa=os.getenv("PASSWORD_2FA"),
    )

    # For example, .show()
    result.qr_image.show()
    result.set_qr_update_callback(lambda img: img.show())

    # Loop it up, until QR login isn't finished
    client.loop.run_until_complete(result.done)

    client.start()

    # Export process itself
    query: TelegramQueryResponse = client.get_songs_data_from_target(
        target="@nillovych"
    )
    query.export(destination=ExportDestination.SPOTIFY)

from settings import ExportDestination
from importTelegram.clients import TelegramMusicExportClient

# Initialize a Singleton, if test_session exists
# If you want to cache a session file
TelegramMusicExportClient.initialize(session="test_session")

# Instantiate client to log in with QRcode
client = TelegramMusicExportClient.instance()
# client.auth(qr_login=True)
client.start()

query = client.get_songs_data_from_target(target="@nillovych")
query.export(destination=ExportDestination.SPOTIFY)

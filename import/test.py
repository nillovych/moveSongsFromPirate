from settings import ExportDestination
from .telegram import TelegramMusicExportClient

client = TelegramMusicExportClient.instance()
client.start()

# lybot_query = client.get_songs_data_from_target("@LyBot")

mm_query = client.get_songs_data_from_target("@nillovych")
print(mm_query.num_unique_songs)
mm_query.export(destination=ExportDestination.SPOTIFY)

# mm_query.add_to_global_export()

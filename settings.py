import os
from pydantic import BaseModel

UNCLASSIFIED_SONG_KEY_NAME = "unclassified"
#
# class SpotifyConfig:
#     CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
#     CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
#     REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


class SpotifyConfig(BaseModel):
    client_id: str = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret: str = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri: str = os.getenv("SPOTIFY_REDIRECT_URI")

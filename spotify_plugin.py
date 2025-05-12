from semantic_kernel.functions import kernel_function
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Optional, Dict, Any

class SpotifyPlugin:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_manager = SpotifyClientCredentials(
            client_id=self.client_id, client_secret=self.client_secret)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    @kernel_function(
        description="Search for an artist by name on Spotify",
        name="search_artist"
    )
    def search_artist(self, artist_name: str, limit: int = 10) -> str:
        """Search for an artist by name."""
        try:
            result = self.sp.search(q=f"artist:{artist_name}", type="artist", limit=limit)
            return str(result)
        except Exception as e:
            return f"Error searching for artist: {str(e)}"

    @kernel_function(
        description="Get artist information by Spotify artist ID",
        name="get_artist"
    )
    def get_artist(self, artist_id: str) -> str:
        try:
            result = self.sp.artist(artist_id)
            return str(result)
        except Exception as e:
            return f"Error getting artist: {str(e)}"

    @kernel_function(
        description="Get albums for an artist by Spotify artist ID",
        name="get_artist_albums"
    )
    def get_artist_albums(self, artist_id: str, limit: int = 10) -> str:
        try:
            result = self.sp.artist_albums(artist_id, limit=limit)
            return str(result)
        except Exception as e:
            return f"Error getting artist albums: {str(e)}"

    @kernel_function(
        description="Get album information by Spotify album ID",
        name="get_album"
    )
    def get_album(self, album_id: str) -> str:
        try:
            result = self.sp.album(album_id)
            return str(result)
        except Exception as e:
            return f"Error getting album: {str(e)}"

    @kernel_function(
        description="Get track information by Spotify track ID",
        name="get_track"
    )
    def get_track(self, track_id: str) -> str:
        try:
            result = self.sp.track(track_id)
            return str(result)
        except Exception as e:
            return f"Error getting track: {str(e)}"

    @kernel_function(
        description="Search for a track by name on Spotify",
        name="search_track"
    )
    def search_track(self, track_name: str, limit: int = 10) -> str:
        try:
            result = self.sp.search(q=f"track:{track_name}", type="track", limit=limit)
            return str(result)
        except Exception as e:
            return f"Error searching for track: {str(e)}"

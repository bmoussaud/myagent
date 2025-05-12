import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Optional, Dict, Any


class SpotifyClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_manager = SpotifyClientCredentials(
            client_id=self.client_id, client_secret=self.client_secret)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def search_artist(self, artist_name: str, limit: int = 10) -> Dict[str, Any]:
        """Search for an artist by name."""
        return self.sp.search(q=f"artist:{artist_name}", type="artist", limit=limit)

    def get_artist(self, artist_id: str) -> Dict[str, Any]:
        """Get artist information by Spotify artist ID."""
        return self.sp.artist(artist_id)

    def get_artist_albums(self, artist_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get albums for an artist by Spotify artist ID."""
        return self.sp.artist_albums(artist_id, limit=limit)

    def get_album(self, album_id: str) -> Dict[str, Any]:
        """Get album information by Spotify album ID."""
        return self.sp.album(album_id)

    def get_track(self, track_id: str) -> Dict[str, Any]:
        """Get track information by Spotify track ID."""
        return self.sp.track(track_id)

    def search_track(self, track_name: str, limit: int = 10) -> Dict[str, Any]:
        """Search for a track by name."""
        return self.sp.search(q=f"track:{track_name}", type="track", limit=limit)

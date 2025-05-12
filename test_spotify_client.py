import os
import unittest
from dotenv import load_dotenv
from spotify_client import SpotifyClient

class TestSpotifyClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise ValueError("SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set in the .env file.")
        cls.spotify = SpotifyClient(client_id, client_secret)

    def test_search_artist(self):
        result = self.spotify.search_artist("Radiohead")
        self.assertIn("artists", result)
        self.assertGreater(len(result["artists"]["items"]), 0)

    def test_get_artist(self):
        # Radiohead's Spotify artist ID
        artist_id = "4Z8W4fKeB5YxbusRsdQVPb"
        result = self.spotify.get_artist(artist_id)
        self.assertEqual(result["id"], artist_id)
        self.assertEqual(result["name"], "Radiohead")

    def test_get_artist_albums(self):
        artist_id = "4Z8W4fKeB5YxbusRsdQVPb"
        result = self.spotify.get_artist_albums(artist_id)
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)

    def test_get_album(self):
        # Radiohead's "OK Computer" album ID
        album_id = "6dVIqQ8qmQ5GBnJ9shOYGE"
        result = self.spotify.get_album(album_id)
        self.assertEqual(result["id"], album_id)
        self.assertEqual(result["name"], "OK Computer")

    def test_get_track(self):
        # "Karma Police" track ID
        track_id = "3SVAN3BRByDmHOhKyIDxfC"
        result = self.spotify.get_track(track_id)
        self.assertEqual(result["id"], track_id)
        self.assertEqual(result["name"], "Karma Police")

    def test_search_track(self):
        result = self.spotify.search_track("Karma Police")
        self.assertIn("tracks", result)
        self.assertGreater(len(result["tracks"]["items"]), 0)

if __name__ == "__main__":
    unittest.main()

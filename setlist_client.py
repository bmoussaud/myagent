
import requests
from typing import Optional, Dict, Any


class SetlistFMClient:
    BASE_URL = "https://api.setlist.fm/rest/1.0"

    def __init__(self, api_key: str, language: str = "en"):
        self.api_key = api_key
        self.language = language
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": self.api_key,
            "Accept": "application/json",
            "Accept-Language": self.language,
            "User-Agent": "setlistfm-python-client/1.0"
        })

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_artist(self, mbid: str) -> Any:
        """Get artist info by Musicbrainz ID (mbid)."""
        return self._get(f"/artist/{mbid}")

    def get_artist_setlists(self, mbid: str, page: int = 1) -> Any:
        """Get setlists for an artist by Musicbrainz ID (mbid)."""
        return self._get(f"/artist/{mbid}/setlists", params={"p": page})

    def search_artists(self, artist_name: str, sort: str = "relevance", page: int = 1) -> Any:
        """Search for artists by name."""
        return self._get("/search/artists", params={"artistName": artist_name, "p": page, "sort": sort})

    def search_setlists(self, artist_mbid: Optional[str] = None, artist_name: Optional[str] = None, city_name: Optional[str] = None, country_code: Optional[str] = None, page: int = 1) -> Any:
        """Search for setlists by artist, city, or country."""
        params = {"p": page}
        if artist_name:
            params["artistName"] = artist_name
        if artist_mbid:
            params["artistMbid"] = artist_mbid
        if city_name:
            params["cityName"] = city_name
        if country_code:
            params["countryCode"] = country_code
        return self._get("/search/setlists", params=params)

    def get_setlist(self, setlist_id: str) -> Any:
        """Get a setlist by its unique setlistId."""
        return self._get(f"/setlist/{setlist_id}")

    def get_venue(self, venue_id: str) -> Any:
        """Get venue info by venueId."""
        return self._get(f"/venue/{venue_id}")

    def get_venue_setlists(self, venue_id: str, page: int = 1) -> Any:
        """Get setlists for a venue by venueId."""
        return self._get(f"/venue/{venue_id}/setlists", params={"p": page})

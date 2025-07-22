"""Shared test utilities and fixtures for all test files."""

from unittest.mock import AsyncMock, Mock

from pydantic import HttpUrl
import pytest

from src.base_client import BaseSpotifyClient
from src.config import SpotifyConfig

# Global test data constants
TEST_CLIENT_ID = "test_client_id"
TEST_CLIENT_SECRET = "test_client_secret"
TEST_REDIRECT_URI = "http://localhost:8888/callback"
TEST_USER_ID = "user123"
TEST_ACCESS_TOKEN = "test_access_token"
TEST_REFRESH_TOKEN = "test_refresh_token"

# Mock token data
MOCK_TOKENS = {
    "access_token": TEST_ACCESS_TOKEN,
    "refresh_token": TEST_REFRESH_TOKEN,
    "expires_in": 3600,
    "token_type": "Bearer",
}

# Mock user data
MOCK_USER_DATA = {
    "id": TEST_USER_ID,
    "display_name": "Test User",
    "external_urls": {"spotify": f"https://open.spotify.com/user/{TEST_USER_ID}"},
    "href": f"https://api.spotify.com/v1/users/{TEST_USER_ID}",
    "uri": f"spotify:user:{TEST_USER_ID}",
}

# Mock artist data
MOCK_ARTIST_DATA = {
    "id": "artist1",
    "name": "Test Artist",
    "external_urls": {"spotify": "https://open.spotify.com/artist/artist1"},
    "href": "https://api.spotify.com/v1/artists/artist1",
    "uri": "spotify:artist:artist1",
}

# Mock album data
MOCK_ALBUM_DATA = {
    "id": "album1",
    "name": "Test Album",
    "album_type": "album",
    "artists": [MOCK_ARTIST_DATA],
    "external_urls": {"spotify": "https://open.spotify.com/album/album1"},
    "href": "https://api.spotify.com/v1/albums/album1",
    "release_date": "2023-01-01",
    "release_date_precision": "day",
    "uri": "spotify:album:album1",
}

# Mock track data
MOCK_TRACK_DATA = {
    "id": "track1",
    "name": "Test Track",
    "album": MOCK_ALBUM_DATA,
    "artists": [MOCK_ARTIST_DATA],
    "disc_number": 1,
    "duration_ms": 180000,
    "explicit": False,
    "external_urls": {"spotify": "https://open.spotify.com/track/track1"},
    "href": "https://api.spotify.com/v1/tracks/track1",
    "is_local": False,
    "popularity": 50,
    "track_number": 1,
    "uri": "spotify:track:track1",
}

# Mock playlist data
MOCK_PLAYLIST_DATA = {
    "id": "playlist1",
    "name": "Test Playlist",
    "collaborative": False,
    "external_urls": {"spotify": "https://open.spotify.com/playlist/playlist1"},
    "href": "https://api.spotify.com/v1/playlists/playlist1",
    "owner": MOCK_USER_DATA,
    "public": True,
    "snapshot_id": "test_snapshot",
    "tracks": {
        "href": "https://api.spotify.com/v1/playlists/playlist1/tracks",
        "items": [],
        "limit": 100,
        "offset": 0,
        "total": 0,
    },
    "uri": "spotify:playlist:playlist1",
}

# Mock playlist track data (for PlaylistTrack objects)
MOCK_PLAYLIST_TRACK_DATA = {
    "added_at": "2023-01-01T00:00:00Z",
    "added_by": MOCK_USER_DATA,
    "is_local": False,
    "track": MOCK_TRACK_DATA,
}


@pytest.fixture
def mock_config():
    """Create a mock SpotifyConfig."""
    config = Mock(spec=SpotifyConfig)
    config.client_id = TEST_CLIENT_ID
    config.client_secret = TEST_CLIENT_SECRET
    config.redirect_uri = HttpUrl(TEST_REDIRECT_URI)
    config.timeout = 30
    config.api_base_url = "https://api.spotify.com/v1"
    config.authorize_url = "https://accounts.spotify.com/authorize"
    config.token_url = "https://accounts.spotify.com/api/token"
    config.scopes = ["playlist-read-private", "user-read-private"]
    config.scopes_string = "playlist-read-private user-read-private"
    config.cache_enabled = True
    config.cache_ttl = 3600
    return config


@pytest.fixture
def mock_tokens():
    """Mock token data."""
    return MOCK_TOKENS.copy()


@pytest.fixture
def mock_user_data():
    """Mock user data."""
    return MOCK_USER_DATA.copy()


@pytest.fixture
def mock_artist_data():
    """Mock artist data."""
    return MOCK_ARTIST_DATA.copy()


@pytest.fixture
def mock_album_data():
    """Mock album data."""
    return MOCK_ALBUM_DATA.copy()


@pytest.fixture
def mock_track_data():
    """Mock track data."""
    return MOCK_TRACK_DATA.copy()


@pytest.fixture
def mock_playlist_data():
    """Mock playlist data."""
    return MOCK_PLAYLIST_DATA.copy()


@pytest.fixture
def mock_spotify_client(mock_config):
    """Create a mock SpotifyClient."""
    client = Mock(spec=BaseSpotifyClient)
    client.config = mock_config
    client._make_request = AsyncMock()
    client._access_token = TEST_ACCESS_TOKEN
    client._refresh_token = TEST_REFRESH_TOKEN
    client._user_id = TEST_USER_ID
    return client


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response."""
    response = Mock()
    response.json.return_value = {}
    response.raise_for_status.return_value = None
    response.status_code = 200
    return response


def create_mock_http_response(data=None, status_code=200, raise_error=None):
    """Helper to create mock HTTP responses."""
    response = Mock()
    response.json.return_value = data or {}
    response.status_code = status_code
    if raise_error:
        response.raise_for_status.side_effect = raise_error
    else:
        response.raise_for_status.return_value = None
    return response

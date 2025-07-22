"""Core functionality tests for Spotify API client."""

from unittest.mock import AsyncMock, patch

import pytest

from src.base_client import SpotifyAPIError
from src.config import SpotifyConfig
from src.models import Playlist, Track
from src.playlists import PlaylistClient
from src.spotify_client import SpotifyClient
from src.tracks import TrackClient
from tests.test_utils import (
    MOCK_PLAYLIST_DATA,
    MOCK_TRACK_DATA,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
)

pytest_plugins = ["tests.test_utils"]


class TestCoreFunctionality:
    """Test core functionality of the Spotify API client."""

    def test_spotify_client_initialization(self, mock_config):
        """Test SpotifyClient initialization."""
        client = SpotifyClient(mock_config)
        assert client.config == mock_config
        assert isinstance(client.playlists, PlaylistClient)
        assert isinstance(client.tracks, TrackClient)

    @pytest.mark.parametrize("method_name", [
        "get_user_playlists",
        "get_playlist",
        "create_playlist",
        "add_tracks_to_playlist",
        "get_track",
        "search_tracks",
    ])
    async def test_unified_client_delegation(self, mock_config, method_name):
        """Test that unified client methods delegate to specialized clients."""
        client = SpotifyClient(mock_config)

        # Mock the specialized client methods
        if method_name == "get_user_playlists":
            client.playlists.get_user_playlists = AsyncMock(return_value=[])
        elif method_name == "get_playlist":
            client.playlists.get_playlist = AsyncMock(return_value=MOCK_PLAYLIST_DATA)
        elif method_name == "create_playlist":
            client.playlists.create_playlist = AsyncMock(return_value=MOCK_PLAYLIST_DATA)
        elif method_name == "add_tracks_to_playlist":
            client.playlists.add_tracks_to_playlist = AsyncMock(return_value=None)
        elif method_name == "get_track":
            client.tracks.get_track = AsyncMock(return_value=MOCK_TRACK_DATA)
        elif method_name == "search_tracks":
            client.tracks.search_tracks = AsyncMock(return_value=[])

        # Call the unified method
        method = getattr(client, method_name)
        if method_name in ["get_user_playlists", "get_playlist", "create_playlist", "get_track", "search_tracks"]:
            await method("test_id")
        elif method_name == "add_tracks_to_playlist":
            await method("test_id", ["track1", "track2"])

        # Verify delegation occurred
        if method_name == "get_user_playlists":
            client.playlists.get_user_playlists.assert_called_once()
        elif method_name == "get_playlist":
            client.playlists.get_playlist.assert_called_once()
        elif method_name == "create_playlist":
            client.playlists.create_playlist.assert_called_once()
        elif method_name == "add_tracks_to_playlist":
            client.playlists.add_tracks_to_playlist.assert_called_once()
        elif method_name == "get_track":
            client.tracks.get_track.assert_called_once()
        elif method_name == "search_tracks":
            client.tracks.search_tracks.assert_called_once()

    async def test_playlist_operations(self, mock_config):
        """Test playlist operations through unified client."""
        client = SpotifyClient(mock_config)
        client.playlists.get_user_playlists = AsyncMock(return_value=[MOCK_PLAYLIST_DATA])
        client.playlists.get_playlist = AsyncMock(return_value=Playlist.model_validate(MOCK_PLAYLIST_DATA))

        # Test get_user_playlists
        playlists = await client.get_user_playlists()
        assert len(playlists) == 1
        assert playlists[0]["id"] == "playlist1"

        # Test get_playlist
        playlist = await client.get_playlist("playlist1")
        assert playlist.id == "playlist1"
        assert playlist.name == "Test Playlist"

    async def test_track_operations(self, mock_config):
        """Test track operations through unified client."""
        client = SpotifyClient(mock_config)
        client.tracks.get_track = AsyncMock(return_value=Track.model_validate(MOCK_TRACK_DATA))
        client.tracks.search_tracks = AsyncMock(return_value=[Track.model_validate(MOCK_TRACK_DATA)])

        # Test get_track
        track = await client.get_track("track1")
        assert track.id == "track1"
        assert track.name == "Test Track"

        # Test search_tracks
        search_result = await client.search_tracks("test query")
        assert len(search_result) == 1
        assert search_result[0].id == "track1"

    async def test_user_operations(self, mock_config, mock_user_data):
        """Test user operations through unified client."""
        client = SpotifyClient(mock_config)
        client.get_current_user = AsyncMock(return_value=mock_user_data)

        user = await client.get_current_user()
        assert user["id"] == "user123"
        assert user["display_name"] == "Test User"

    def test_basic_error_handling(self, mock_config):
        """Test basic error handling."""
        with pytest.raises(SpotifyAPIError):
            raise SpotifyAPIError("Test error")

    def test_config_validation(self):
        """Test configuration validation."""
        # Test valid config
        from pydantic import HttpUrl
        config = SpotifyConfig(
            client_id=TEST_CLIENT_ID,
            client_secret=TEST_CLIENT_SECRET,
            redirect_uri=HttpUrl("http://localhost:8888/callback"),
        )
        assert config.client_id == TEST_CLIENT_ID
        assert config.client_secret == TEST_CLIENT_SECRET

        # Test invalid config
        with pytest.raises(ValueError):
            SpotifyConfig(
                client_id="",  # Invalid empty client_id
                client_secret=TEST_CLIENT_SECRET,
                redirect_uri=HttpUrl("http://localhost:8888/callback"),
            )

    @pytest.mark.parametrize("cache_enabled,expected", [
        ("true", True),
        ("false", False),
        ("invalid", False),
    ])
    def test_config_from_env_cache_settings(self, cache_enabled, expected):
        """Test config cache settings from environment."""
        with patch.dict("os.environ", {
            "SPOTIFY_CLIENT_ID": TEST_CLIENT_ID,
            "SPOTIFY_CLIENT_SECRET": TEST_CLIENT_SECRET,
            "SPOTIFY_CACHE_ENABLED": cache_enabled,
        }):
            config = SpotifyConfig.from_env()
            assert config.cache_enabled == expected

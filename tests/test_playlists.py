"""Unit tests for PlaylistClient."""

from unittest.mock import AsyncMock, Mock

import pytest

from src.base_client import BaseSpotifyClient
from src.playlists import PlaylistClient
from tests.test_utils import MOCK_PLAYLIST_DATA


class TestPlaylistClient:
    """Test PlaylistClient class."""

    @pytest.fixture
    def mock_base_client(self, mock_config):
        """Create a mock BaseSpotifyClient."""
        base_client = Mock(spec=BaseSpotifyClient)
        base_client.config = mock_config
        base_client._user_id = "test_user_id"
        base_client._make_request = AsyncMock()
        base_client.get_current_user = AsyncMock()
        return base_client

    @pytest.fixture
    def playlist_client(self, mock_base_client):
        """Create a PlaylistClient instance."""
        return PlaylistClient(mock_base_client)

    def test_playlist_client_init(self, mock_base_client):
        """Test PlaylistClient initialization."""
        client = PlaylistClient(mock_base_client)
        assert client._client == mock_base_client

    async def test_get_user_playlists_with_user_id(
        self, playlist_client, mock_base_client
    ):
        """Test get_user_playlists with explicit user_id."""
        mock_response = {
            "items": [
                {"id": "playlist1", "name": "Playlist 1"},
                {"id": "playlist2", "name": "Playlist 2"},
            ]
        }
        mock_base_client._make_request.return_value = mock_response

        result = await playlist_client.get_user_playlists(
            "explicit_user_id", limit=10, offset=5
        )

        mock_base_client._make_request.assert_called_once_with(
            "GET",
            "/users/explicit_user_id/playlists",
            params={"limit": "10", "offset": "5"},
        )
        assert result == mock_response["items"]

    async def test_get_user_playlists_with_cached_user_id(
        self, playlist_client, mock_base_client
    ):
        """Test get_user_playlists with cached user_id."""
        mock_response = {
            "items": [
                {"id": "playlist1", "name": "Playlist 1"},
            ]
        }
        mock_base_client._make_request.return_value = mock_response

        result = await playlist_client.get_user_playlists()

        mock_base_client._make_request.assert_called_once_with(
            "GET",
            "/users/test_user_id/playlists",
            params={"limit": "20", "offset": "0"},
        )
        assert result == mock_response["items"]

    async def test_get_user_playlists_with_current_user(
        self, playlist_client, mock_base_client
    ):
        """Test get_user_playlists with current user lookup."""
        mock_base_client._user_id = None
        mock_user = Mock()
        mock_user.id = "current_user_id"
        mock_base_client.get_current_user.return_value = mock_user

        mock_response = {"items": [{"id": "playlist1", "name": "Playlist 1"}]}
        mock_base_client._make_request.return_value = mock_response

        result = await playlist_client.get_user_playlists()

        mock_base_client.get_current_user.assert_called_once()
        mock_base_client._make_request.assert_called_once_with(
            "GET",
            "/users/current_user_id/playlists",
            params={"limit": "20", "offset": "0"},
        )
        assert result == mock_response["items"]

    async def test_get_playlist(self, playlist_client, mock_base_client):
        """Test get_playlist method."""
        mock_base_client._make_request.return_value = MOCK_PLAYLIST_DATA

        result = await playlist_client.get_playlist("playlist1")

        mock_base_client._make_request.assert_called_once_with(
            "GET", "/playlists/playlist1", params={}
        )
        assert result.id == "playlist1"

    async def test_create_playlist_with_user_id(
        self, playlist_client, mock_base_client
    ):
        """Test create_playlist with explicit user_id."""
        mock_base_client._make_request.return_value = MOCK_PLAYLIST_DATA

        result = await playlist_client.create_playlist(
            "New Playlist",
            "Test Description",
            user_id="explicit_user_id",
            public=True,
            collaborative=False,
        )

        mock_base_client._make_request.assert_called_once_with(
            "POST",
            "/users/explicit_user_id/playlists",
            data={
                "name": "New Playlist",
                "description": "Test Description",
                "public": True,
                "collaborative": False,
            },
        )
        assert result.id == "playlist1"

    async def test_create_playlist_with_cached_user_id(
        self, playlist_client, mock_base_client
    ):
        """Test create_playlist with cached user_id."""
        mock_base_client._make_request.return_value = MOCK_PLAYLIST_DATA

        result = await playlist_client.create_playlist(
            "New Playlist", "Test Description"
        )

        mock_base_client._make_request.assert_called_once_with(
            "POST",
            "/users/test_user_id/playlists",
            data={
                "name": "New Playlist",
                "description": "Test Description",
                "public": True,
                "collaborative": False,
            },
        )
        assert result.id == "playlist1"

    async def test_create_playlist_with_current_user(
        self, playlist_client, mock_base_client
    ):
        """Test create_playlist with current user lookup."""
        mock_base_client._user_id = None
        mock_user = Mock()
        mock_user.id = "current_user_id"
        mock_base_client.get_current_user.return_value = mock_user
        mock_base_client._make_request.return_value = MOCK_PLAYLIST_DATA

        result = await playlist_client.create_playlist(
            "New Playlist", "Test Description"
        )

        mock_base_client.get_current_user.assert_called_once()
        mock_base_client._make_request.assert_called_once_with(
            "POST",
            "/users/current_user_id/playlists",
            data={
                "name": "New Playlist",
                "description": "Test Description",
                "public": True,
                "collaborative": False,
            },
        )
        assert result.id == "playlist1"

    async def test_add_tracks_to_playlist(self, playlist_client, mock_base_client):
        """Test add_tracks_to_playlist method."""
        mock_base_client._make_request.return_value = {"snapshot_id": "new_snapshot"}

        result = await playlist_client.add_tracks_to_playlist(
            "playlist1", ["track1", "track2"], position=5
        )

        mock_base_client._make_request.assert_called_once_with(
            "POST",
            "/playlists/playlist1/tracks",
            data={"uris": ["track1", "track2"], "position": 5},
        )
        assert result == "new_snapshot"

    async def test_add_tracks_to_playlist_no_position(
        self, playlist_client, mock_base_client
    ):
        """Test add_tracks_to_playlist without position."""
        mock_base_client._make_request.return_value = {"snapshot_id": "new_snapshot"}

        result = await playlist_client.add_tracks_to_playlist(
            "playlist1", ["track1", "track2"]
        )

        mock_base_client._make_request.assert_called_once_with(
            "POST", "/playlists/playlist1/tracks", data={"uris": ["track1", "track2"]}
        )
        assert result == "new_snapshot"

    async def test_remove_tracks_from_playlist(self, playlist_client, mock_base_client):
        """Test remove_tracks_from_playlist method."""
        mock_base_client._make_request.return_value = {"snapshot_id": "new_snapshot"}

        result = await playlist_client.remove_tracks_from_playlist(
            "playlist1", ["track1", "track2"], "old_snapshot"
        )

        mock_base_client._make_request.assert_called_once_with(
            "DELETE",
            "/playlists/playlist1/tracks",
            data={"uris": ["track1", "track2"], "snapshot_id": "old_snapshot"},
        )
        assert result == "new_snapshot"

    async def test_remove_tracks_from_playlist_no_snapshot(
        self, playlist_client, mock_base_client
    ):
        """Test remove_tracks_from_playlist without snapshot."""
        mock_base_client._make_request.return_value = {"snapshot_id": "new_snapshot"}

        result = await playlist_client.remove_tracks_from_playlist(
            "playlist1", ["track1", "track2"]
        )

        mock_base_client._make_request.assert_called_once_with(
            "DELETE", "/playlists/playlist1/tracks", data={"uris": ["track1", "track2"]}
        )
        assert result == "new_snapshot"

    async def test_update_playlist(self, playlist_client, mock_base_client):
        """Test update_playlist method."""
        mock_base_client._make_request.return_value = None

        result = await playlist_client.update_playlist(
            "playlist1",
            name="Updated Name",
            description="Updated Description",
            public=False,
            collaborative=True,
        )

        mock_base_client._make_request.assert_called_once_with(
            "PUT",
            "/playlists/playlist1",
            data={
                "name": "Updated Name",
                "description": "Updated Description",
                "public": False,
                "collaborative": True,
            },
        )
        assert result is None

    async def test_update_playlist_partial(self, playlist_client, mock_base_client):
        """Test update_playlist with partial data."""
        mock_base_client._make_request.return_value = None

        result = await playlist_client.update_playlist("playlist1", name="Updated Name")

        mock_base_client._make_request.assert_called_once_with(
            "PUT", "/playlists/playlist1", data={"name": "Updated Name"}
        )
        assert result is None

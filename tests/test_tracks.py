"""Unit tests for TrackClient."""

from unittest.mock import AsyncMock, Mock

import pytest

from src.base_client import BaseSpotifyClient
from src.tracks import TrackClient
from tests.test_utils import MOCK_TRACK_DATA


class TestTrackClient:
    """Test TrackClient class."""

    @pytest.fixture
    def mock_base_client(self):
        """Create a mock BaseSpotifyClient."""
        base_client = Mock(spec=BaseSpotifyClient)
        base_client._make_request = AsyncMock()
        base_client.search = AsyncMock()
        return base_client

    @pytest.fixture
    def track_client(self, mock_base_client):
        """Create a TrackClient instance."""
        return TrackClient(mock_base_client)

    def test_track_client_init(self, mock_base_client):
        """Test TrackClient initialization."""
        client = TrackClient(mock_base_client)
        assert client._client == mock_base_client

    async def test_get_track(self, track_client, mock_base_client):
        """Test get_track method."""
        mock_base_client._make_request.return_value = MOCK_TRACK_DATA

        result = await track_client.get_track("track1")

        mock_base_client._make_request.assert_called_once_with("GET", "/tracks/track1")
        assert result.id == "track1"
        assert result.name == "Test Track"

    async def test_search_tracks_with_results(self, track_client, mock_base_client):
        """Test search_tracks with results."""
        mock_search_response = {
            "tracks": {
                "items": [MOCK_TRACK_DATA],
                "total": 1,
                "limit": 20,
                "offset": 0
            }
        }
        mock_base_client.search.return_value = mock_search_response

        result = await track_client.search_tracks("test query", limit=10, offset=5)

        mock_base_client.search.assert_called_once_with(
            "test query", ["track"], None, 10, 5
        )
        assert len(result) == 1
        assert result[0].id == "track1"

    async def test_search_tracks_no_results(self, track_client, mock_base_client):
        """Test search_tracks with no results."""
        mock_search_response = {"tracks": {"items": [], "total": 0, "limit": 20, "offset": 0}}
        mock_base_client.search.return_value = mock_search_response

        result = await track_client.search_tracks("nonexistent")

        assert result == []
        assert len(result) == 0

    async def test_search_tracks_no_tracks_key(self, track_client, mock_base_client):
        """Test search_tracks when response has no tracks key."""
        mock_search_response = {"error": "No tracks found"}
        mock_base_client.search.return_value = mock_search_response

        result = await track_client.search_tracks("test")

        assert result == []

    async def test_search_tracks_no_items(self, track_client, mock_base_client):
        """Test search_tracks when tracks has no items."""
        mock_search_response = {"tracks": {"total": 0, "limit": 20, "offset": 0}}
        mock_base_client.search.return_value = mock_search_response

        result = await track_client.search_tracks("test")

        assert result == []

    async def test_search_tracks_default_parameters(self, track_client, mock_base_client):
        """Test search_tracks with default parameters."""
        mock_search_response = {"tracks": {"items": [], "total": 0, "limit": 20, "offset": 0}}
        mock_base_client.search.return_value = mock_search_response

        result = await track_client.search_tracks("test")

        mock_base_client.search.assert_called_once_with(
            "test", ["track"], None, 20, 0
        )
        assert result == []

"""Streamlined tests for Pydantic models."""

from pydantic import ValidationError
import pytest

from src.models import Album, Artist, Playlist, Track, User

pytest_plugins = ["tests.test_utils"]


class TestModels:
    """Test Pydantic models with focused, parameterized tests."""

    def test_user_model_creation(self, mock_user_data):
        """Test User model creation and validation."""
        user = User.model_validate(mock_user_data)
        assert user.id == "user123"
        assert user.display_name == "Test User"
        assert user.uri == "spotify:user:user123"

    @pytest.mark.parametrize(
        "invalid_uri",
        [
            "spotify:track:track1",  # Wrong type
            "http://example.com/user",  # Not spotify URI
            "invalid:user:user123",  # Wrong format
        ],
    )
    def test_user_model_invalid_uri(self, mock_user_data, invalid_uri):
        """Test User model with invalid URIs."""
        invalid_data = mock_user_data.copy()
        invalid_data["uri"] = invalid_uri

        with pytest.raises(ValidationError):
            User.model_validate(invalid_data)

    def test_artist_model_creation(self, mock_artist_data):
        """Test Artist model creation and validation."""
        artist = Artist.model_validate(mock_artist_data)
        assert artist.id == "artist1"
        assert artist.name == "Test Artist"
        assert artist.uri == "spotify:artist:artist1"

    def test_album_model_creation(self, mock_album_data):
        """Test Album model creation and validation."""
        album = Album.model_validate(mock_album_data)
        assert album.id == "album1"
        assert album.name == "Test Album"
        assert album.album_type == "album"
        assert len(album.artists) == 1
        assert album.artists[0].id == "artist1"

    def test_track_model_creation(self, mock_track_data):
        """Test Track model creation and validation."""
        track = Track.model_validate(mock_track_data)
        assert track.id == "track1"
        assert track.name == "Test Track"
        assert track.album.id == "album1"
        assert len(track.artists) == 1
        assert track.artists[0].id == "artist1"
        assert track.duration_ms == 180000

    def test_playlist_model_creation(self, mock_playlist_data):
        """Test Playlist model creation and validation."""
        playlist = Playlist.model_validate(mock_playlist_data)
        assert playlist.id == "playlist1"
        assert playlist.name == "Test Playlist"
        assert playlist.owner.id == "user123"
        assert playlist.public is True
        assert playlist.collaborative is False

    def test_playlist_to_simplified(self, mock_playlist_data):
        """Test Playlist.to_simplified method."""
        playlist = Playlist.model_validate(mock_playlist_data)
        simplified = playlist.to_simplified()

        assert simplified["id"] == "playlist1"
        assert simplified["name"] == "Test Playlist"
        assert simplified["owner"].id == "user123"

    @pytest.mark.parametrize(
        "duration_ms,expected_seconds,expected_formatted",
        [
            (60000, 60.0, "1:00"),
            (125000, 125.0, "2:05"),
            (3600000, 3600.0, "60:00"),
            (0, 0.0, "0:00"),
        ],
    )
    def test_track_duration_properties(
        self, mock_track_data, duration_ms, expected_seconds, expected_formatted
    ):
        """Test Track duration properties."""
        track_data = mock_track_data.copy()
        track_data["duration_ms"] = duration_ms
        track = Track.model_validate(track_data)

        assert track.duration_seconds == expected_seconds
        assert track.duration_formatted == expected_formatted

    @pytest.mark.parametrize(
        "track_count,expected_duration",
        [
            (0, 0),
            (1, 180000),
            (3, 540000),
        ],
    )
    def test_playlist_duration_properties(
        self, mock_playlist_data, track_count, expected_duration
    ):
        """Test Playlist duration properties."""
        from tests.test_utils import MOCK_PLAYLIST_TRACK_DATA

        playlist_data = mock_playlist_data.copy()
        if track_count > 0:
            playlist_data["tracks"]["items"] = [MOCK_PLAYLIST_TRACK_DATA] * track_count
            playlist_data["tracks"]["total"] = track_count
        playlist = Playlist.model_validate(playlist_data)

        assert playlist.duration_ms == expected_duration
        if expected_duration == 0:
            assert playlist.duration_formatted == "0m"
        else:
            assert playlist.duration_formatted == f"{expected_duration // 60000}m"

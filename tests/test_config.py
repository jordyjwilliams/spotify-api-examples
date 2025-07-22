"""Unit tests for SpotifyConfig."""

import os
from unittest.mock import patch

from pydantic import HttpUrl, ValidationError
import pytest

from src.config import SpotifyConfig
from tests.test_utils import TEST_CLIENT_ID, TEST_CLIENT_SECRET, TEST_REDIRECT_URI


class TestSpotifyConfig:
    """Test SpotifyConfig class."""

    def test_spotify_config_creation(self):
        """Test creating SpotifyConfig with valid data."""
        config = SpotifyConfig(
            client_id=TEST_CLIENT_ID,
            client_secret=TEST_CLIENT_SECRET,
            redirect_uri=HttpUrl(TEST_REDIRECT_URI),
        )

        assert config.client_id == TEST_CLIENT_ID
        assert config.client_secret == TEST_CLIENT_SECRET
        assert str(config.redirect_uri) == TEST_REDIRECT_URI
        assert config.user_id is None
        assert config.cache_enabled is True
        assert config.cache_ttl == 3600
        assert config.api_base_url == "https://api.spotify.com/v1"
        assert config.auth_base_url == "https://accounts.spotify.com"
        assert config.token_url == "https://accounts.spotify.com/api/token"
        assert config.authorize_url == "https://accounts.spotify.com/authorize"
        assert config.timeout == 30
        assert config.max_retries == 3

    def test_spotify_config_with_optional_fields(self):
        """Test creating SpotifyConfig with optional fields."""
        config = SpotifyConfig(
            client_id=TEST_CLIENT_ID,
            client_secret=TEST_CLIENT_SECRET,
            redirect_uri=HttpUrl(TEST_REDIRECT_URI),
            user_id="test_user_id",
            cache_enabled=False,
            cache_ttl=7200,
            timeout=60,
            max_retries=5,
        )

        assert config.user_id == "test_user_id"
        assert config.cache_enabled is False
        assert config.cache_ttl == 7200
        assert config.timeout == 60
        assert config.max_retries == 5

    def test_validate_credentials_valid(self):
        """Test validate_credentials with valid credentials."""
        result = SpotifyConfig.validate_credentials("valid_client_id")
        assert result == "valid_client_id"

    def test_validate_credentials_empty(self):
        """Test validate_credentials with empty string."""
        with pytest.raises(
            ValueError, match="Client ID and Client Secret cannot be empty"
        ):
            SpotifyConfig.validate_credentials("")

    def test_validate_credentials_whitespace(self):
        """Test validate_credentials with whitespace only."""
        with pytest.raises(
            ValueError, match="Client ID and Client Secret cannot be empty"
        ):
            SpotifyConfig.validate_credentials("   ")

    def test_validate_credentials_strips_whitespace(self):
        """Test validate_credentials strips whitespace."""
        result = SpotifyConfig.validate_credentials("  test_id  ")
        assert result == "test_id"

    def test_validate_redirect_uri_valid_http(self):
        """Test validate_redirect_uri with valid HTTP URL."""
        uri = HttpUrl("http://localhost:8888/callback")
        result = SpotifyConfig.validate_redirect_uri(uri)
        assert result == uri

    def test_validate_redirect_uri_valid_https(self):
        """Test validate_redirect_uri with valid HTTPS URL."""
        uri = HttpUrl("https://example.com/callback")
        result = SpotifyConfig.validate_redirect_uri(uri)
        assert result == uri

    def test_validate_redirect_uri_invalid(self):
        """Test validate_redirect_uri with invalid URL."""
        with pytest.raises(ValidationError):
            HttpUrl("ftp://example.com/callback")

    def test_scopes_string(self):
        """Test scopes_string property."""
        config = SpotifyConfig(
            client_id=TEST_CLIENT_ID,
            client_secret=TEST_CLIENT_SECRET,
            redirect_uri=HttpUrl(TEST_REDIRECT_URI),
            scopes=["playlist-read-private", "user-read-private"],
        )
        assert config.scopes_string == "playlist-read-private user-read-private"

    @patch.dict(
        os.environ,
        {
            "SPOTIFY_CLIENT_ID": "env_client_id",
            "SPOTIFY_CLIENT_SECRET": "env_client_secret",
            "SPOTIFY_REDIRECT_URI": "http://localhost:9999/callback",
            "SPOTIFY_USER_ID": "env_user_id",
            "SPOTIFY_CACHE_ENABLED": "false",
            "SPOTIFY_CACHE_TTL": "7200",
            "SPOTIFY_TIMEOUT": "60",
            "SPOTIFY_MAX_RETRIES": "5",
        },
    )
    def test_from_env_with_all_variables(self):
        """Test from_env with all environment variables."""
        config = SpotifyConfig.from_env()

        assert config.client_id == "env_client_id"
        assert config.client_secret == "env_client_secret"
        assert str(config.redirect_uri) == "http://localhost:9999/callback"
        assert config.user_id == "env_user_id"
        assert config.cache_enabled is False
        assert config.cache_ttl == 7200
        assert config.timeout == 60
        assert config.max_retries == 5

    @patch.dict(
        os.environ,
        {
            "SPOTIFY_CLIENT_ID": "env_client_id",
            "SPOTIFY_CLIENT_SECRET": "env_client_secret",
        },
        clear=True,
    )
    def test_from_env_with_minimal_variables(self):
        """Test from_env with minimal environment variables."""
        config = SpotifyConfig.from_env()

        assert config.client_id == "env_client_id"
        assert config.client_secret == "env_client_secret"
        assert str(config.redirect_uri) == "http://127.0.0.1:8000/callback"
        assert config.user_id is None
        assert config.cache_enabled is True
        assert config.cache_ttl == 3600
        assert config.timeout == 30
        assert config.max_retries == 3

    @patch.dict(
        os.environ,
        {
            "SPOTIFY_CLIENT_ID": "env_client_id",
            "SPOTIFY_CLIENT_SECRET": "env_client_secret",
            "SPOTIFY_CACHE_ENABLED": "true",
        },
        clear=True,
    )
    def test_from_env_cache_enabled_true(self):
        """Test from_env with cache_enabled=true."""
        config = SpotifyConfig.from_env()
        assert config.cache_enabled is True

    @patch.dict(
        os.environ,
        {
            "SPOTIFY_CLIENT_ID": "env_client_id",
            "SPOTIFY_CLIENT_SECRET": "env_client_secret",
            "SPOTIFY_CACHE_ENABLED": "false",
        },
        clear=True,
    )
    def test_from_env_cache_enabled_false(self):
        """Test from_env with cache_enabled=false."""
        config = SpotifyConfig.from_env()
        assert config.cache_enabled is False

    @patch.dict(
        os.environ,
        {
            "SPOTIFY_CLIENT_ID": "env_client_id",
            "SPOTIFY_CLIENT_SECRET": "env_client_secret",
            "SPOTIFY_CACHE_ENABLED": "invalid",
        },
        clear=True,
    )
    def test_from_env_cache_enabled_invalid(self):
        """Test from_env with invalid cache_enabled value."""
        config = SpotifyConfig.from_env()
        assert config.cache_enabled is False  # Default value

    @patch.dict(
        os.environ,
        {
            "SPOTIFY_CLIENT_ID": "env_client_id",
            "SPOTIFY_CLIENT_SECRET": "env_client_secret",
            "SPOTIFY_CACHE_TTL": "invalid",
        },
        clear=True,
    )
    def test_from_env_cache_ttl_invalid(self):
        """Test from_env with invalid cache_ttl value."""
        with pytest.raises(ValueError, match="invalid literal for int"):
            SpotifyConfig.from_env()

    @patch.dict(
        os.environ,
        {
            "SPOTIFY_CLIENT_ID": "env_client_id",
            "SPOTIFY_CLIENT_SECRET": "env_client_secret",
            "SPOTIFY_TIMEOUT": "invalid",
        },
        clear=True,
    )
    def test_from_env_timeout_invalid(self):
        """Test from_env with invalid timeout value."""
        with pytest.raises(ValueError, match="invalid literal for int"):
            SpotifyConfig.from_env()

    @patch.dict(
        os.environ,
        {
            "SPOTIFY_CLIENT_ID": "env_client_id",
            "SPOTIFY_CLIENT_SECRET": "env_client_secret",
            "SPOTIFY_MAX_RETRIES": "invalid",
        },
        clear=True,
    )
    def test_from_env_max_retries_invalid(self):
        """Test from_env with invalid max_retries value."""
        with pytest.raises(ValueError, match="invalid literal for int"):
            SpotifyConfig.from_env()

    def test_spotify_config_validation_error(self):
        """Test SpotifyConfig validation error."""
        with pytest.raises(ValidationError):
            SpotifyConfig(
                client_id="",  # Invalid empty client_id
                client_secret=TEST_CLIENT_SECRET,
                redirect_uri=HttpUrl(TEST_REDIRECT_URI),
            )

    def test_spotify_config_validation_error_secret(self):
        """Test SpotifyConfig validation error with empty secret."""
        with pytest.raises(ValidationError):
            SpotifyConfig(
                client_id=TEST_CLIENT_ID,
                client_secret="",  # Invalid empty client_secret
                redirect_uri=HttpUrl(TEST_REDIRECT_URI),
            )

    def test_spotify_config_validation_error_redirect_uri(self):
        """Test SpotifyConfig validation error with invalid redirect_uri."""
        with pytest.raises(ValidationError):
            SpotifyConfig(
                client_id=TEST_CLIENT_ID,
                client_secret=TEST_CLIENT_SECRET,
                redirect_uri=HttpUrl("ftp://invalid-uri"),  # Invalid URI scheme
            )

"""Configuration management for Spotify API client.

Sets configuration from environment variables.
"""

import os

from dotenv import load_dotenv
from pydantic import BaseModel, HttpUrl, field_validator

# Load environment variables from .env file
load_dotenv()

DEFAULT_REDIRECT_URI = "http://127.0.0.1:8000/callback"


class SpotifyConfig(BaseModel):
    """Spotify API configuration."""

    # Required credentials
    client_id: str
    client_secret: str
    redirect_uri: HttpUrl

    # Optional settings
    user_id: str | None = None
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour default
    # TODO: consider adding reloading etc for expired tokens.

    # API settings
    api_base_url: str = "https://api.spotify.com/v1"
    auth_base_url: str = "https://accounts.spotify.com"
    token_url: str = "https://accounts.spotify.com/api/token"
    authorize_url: str = "https://accounts.spotify.com/authorize"

    # Scopes for playlist operations
    scopes: list[str] = [
        "playlist-read-private",
        "playlist-read-collaborative",
        "playlist-modify-public",
        "playlist-modify-private",
        "user-read-private",
        "user-read-email",
    ]

    # HTTP settings
    # TODO: These could additionally be set in env vars.
    # NOTE: Out of scope for now.
    timeout: int = 30
    max_retries: int = 3

    @field_validator("client_id", "client_secret")
    @classmethod
    def validate_credentials(cls, v: str) -> str:
        """Validate that credentials are not empty."""
        if not v or v.strip() == "":
            raise ValueError("Client ID and Client Secret cannot be empty")
        return v.strip()

    @field_validator("redirect_uri")
    @classmethod
    def validate_redirect_uri(cls, v: HttpUrl) -> HttpUrl:
        """Validate redirect URI format."""
        if not str(v).startswith(("http://", "https://")):
            raise ValueError("Redirect URI must be a valid HTTP/HTTPS URL")
        return v

    @property
    def scopes_string(self) -> str:
        """Get scopes as space-separated string."""
        return " ".join(self.scopes)

    @classmethod
    def from_env(cls) -> "SpotifyConfig":
        """Create configuration from environment variables."""
        from pydantic import HttpUrl

        redirect_uri_str = os.getenv("SPOTIFY_REDIRECT_URI", DEFAULT_REDIRECT_URI)
        redirect_uri = HttpUrl(redirect_uri_str)

        return cls(
            client_id=os.getenv("SPOTIFY_CLIENT_ID", ""),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET", ""),
            redirect_uri=redirect_uri,
            user_id=os.getenv("SPOTIFY_USER_ID"),
            cache_enabled=os.getenv("SPOTIFY_CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.getenv("SPOTIFY_CACHE_TTL", "3600")),
            timeout=int(os.getenv("SPOTIFY_TIMEOUT", "30")),
            max_retries=int(os.getenv("SPOTIFY_MAX_RETRIES", "3")),
        )

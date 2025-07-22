"""Main Spotify API client for playlist operations."""
import logging
import httpx
from pydantic import ValidationError

from .config import SpotifyConfig
logger = logging.getLogger(__name__)


class SpotifyAuthError(Exception):
    """Raised when authentication fails."""
    pass


class SpotifyAPIError(Exception):
    """Raised when API calls fail."""

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        response: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class SpotifyClient:
    """Async Spotify API client with secure authentication."""

    def __init__(self, config: SpotifyConfig | None = None):
        self.config = config or SpotifyConfig.from_env()
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._client: httpx.AsyncClient | None = None
        self._user_id: str | None = None

        # Validate configuration
        try:
            self.config.validate_credentials(self.config.client_id)
            self.config.validate_credentials(self.config.client_secret)
        except ValidationError as e:
            raise SpotifyAuthError(f"Invalid configuration: {e}") from e

    async def __aenter__(self):
        """Async context manager entry.
        Ensures authentication happens automatically when entering the context.
        """
        await self._ensure_authenticated()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit.
        Ensures proper cleanup of the HTTP client when exiting the context
        """
        await self.close()


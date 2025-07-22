"""Main Spotify API client for playlist operations."""
import logging
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


"""Main Spotify API client for playlist operations."""
import logging
logger = logging.getLogger(__name__)


class SpotifyAuthError(Exception):
    """Raised when authentication fails."""
    pass


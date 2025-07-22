"""Source code for Spotify Web API Playlist Endpoints."""

from pathlib import Path
import tomllib

from .models import Playlist, Track, User
from .spotify_client import SpotifyClient
from .base_client import SpotifyAuthError, SpotifyAPIError


def _get_version() -> str:
    """Get version from pyproject.toml."""
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    # NOTE: should not hit this ever. But let's be safe.
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "0.1.0"  # fallback version


__version__ = _get_version()

__all__ = [
    "SpotifyClient",
    "Playlist",
    "Track",
    "User",
    "SpotifyAuthError",
    "SpotifyAPIError",
]

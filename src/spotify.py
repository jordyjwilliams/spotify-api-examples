"""Main Spotify API client for playlist operations."""

import base64
import json
import logging
import secrets
import webbrowser
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx
from pydantic import ValidationError

from .auth_server import AuthServer
from .config import SpotifyConfig
from .models import (
    Playlist,
    SearchResult,
    Track,
    User,
)

logger = logging.getLogger(__name__)

# Token cache file
TOKEN_CACHE_FILE = Path(".spotify_token_cache.json")


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

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """
        Get or create HTTP client.

        Uses httpx over requests/aiohttp because:
        - Native async/await support (requests is sync-only)
        - Simple requests-like API (aiohttp is more verbose)
        - HTTP/2 support and connection pooling
        - Type hints and modern design
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            )
        return self._client

    def _load_cached_tokens(self) -> bool:
        """Load tokens from cache file if available."""
        try:
            if TOKEN_CACHE_FILE.exists():
                with open(TOKEN_CACHE_FILE) as f:
                    token_data = json.load(f)
                    self._access_token = token_data.get("access_token")
                    self._refresh_token = token_data.get("refresh_token")
                    logger.info("Loaded tokens from cache")
                    return True
        except Exception as e:
            logger.warning(f"Failed to load cached tokens: {e}")
        return False

    def _save_tokens_to_cache(self):
        """Save current tokens to cache file."""
        try:
            if self._access_token and self._refresh_token:
                token_data = {
                    "access_token": self._access_token,
                    "refresh_token": self._refresh_token,
                }
                with open(TOKEN_CACHE_FILE, "w") as f:
                    json.dump(token_data, f)
                logger.info("Saved tokens to cache")
        except Exception as e:
            logger.warning(f"Failed to save tokens to cache: {e}")

    def _clear_cached_tokens(self):
        """Clear cached tokens."""
        try:
            if TOKEN_CACHE_FILE.exists():
                TOKEN_CACHE_FILE.unlink()
                logger.info("Cleared cached tokens")
        except Exception as e:
            logger.warning(f"Failed to clear cached tokens: {e}")

    def clear_auth_cache(self):
        """Clear the authentication cache. Useful for forcing re-authentication."""
        self._access_token = None
        self._refresh_token = None
        self._clear_cached_tokens()
        logger.info("Authentication cache cleared")

    async def _ensure_authenticated(self):
        """Ensure we have a valid access token."""
        if not self._access_token:
            # Try to load from cache first
            if not self._load_cached_tokens():
                await self.authenticate()
            else:
                # Verify the cached token is still valid
                try:
                    await self._get_user_id()
                except Exception:
                    logger.info("Cached token is invalid, re-authenticating...")
                    self._clear_cached_tokens()
                    await self.authenticate()

    async def authenticate(self, force_refresh: bool = False):
        """Authenticate with Spotify using Authorization Code flow."""
        if self._access_token and not force_refresh:
            return

        # Generate state for security
        state = secrets.token_urlsafe(32)

        # Build authorization URL
        auth_params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "redirect_uri": str(self.config.redirect_uri),
            "state": state,
            "scope": self.config.scopes_string,
        }

        auth_url = f"{self.config.authorize_url}?{urlencode(auth_params)}"

        async with AuthServer(config=self.config).serve() as auth_server:
            # Open browser for user authorization
            print("Opening browser for Spotify authorization...")
            print(f"If browser doesn't open, visit: {auth_url}")
            webbrowser.open(auth_url)

            # Wait for the authorization callback
            code = await auth_server.wait_for_auth(state)

        # Exchange code for tokens
        await self._exchange_code_for_tokens(code)

        # Get user ID
        await self._get_user_id()

    async def _exchange_code_for_tokens(self, code: str):
        """Exchange authorization code for access and refresh tokens."""
        # Prepare request
        auth_header = base64.b64encode(
            f"{self.config.client_id}:{self.config.client_secret}".encode()
        ).decode()

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": str(self.config.redirect_uri),
        }

        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Make request
        response = await self.client.post(
            self.config.token_url, data=data, headers=headers
        )

        if response.status_code != 200:
            raise SpotifyAuthError(f"Token exchange failed: {response.text}")

        token_data = response.json()
        self._access_token = token_data["access_token"]
        self._refresh_token = token_data.get("refresh_token")

        # Save tokens to cache
        self._save_tokens_to_cache()

        logger.info("Successfully obtained access token")

    async def _refresh_access_token(self):
        """Refresh the access token using refresh token."""
        if not self._refresh_token:
            raise SpotifyAuthError("No refresh token available")

        auth_header = base64.b64encode(
            f"{self.config.client_id}:{self.config.client_secret}".encode()
        ).decode()

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
        }

        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = await self.client.post(
            self.config.token_url, data=data, headers=headers
        )

        if response.status_code != 200:
            raise SpotifyAuthError(f"Token refresh failed: {response.text}")

        token_data = response.json()
        self._access_token = token_data["access_token"]

        # Update refresh token if provided
        if "refresh_token" in token_data:
            self._refresh_token = token_data["refresh_token"]

        # Save updated tokens to cache
        self._save_tokens_to_cache()

        logger.info("Successfully refreshed access token")

    async def _get_user_id(self):
        """Get current user ID."""
        user = await self.get_current_user()
        self._user_id = user.id

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        retries: int = 0,
    ) -> dict[str, Any]:
        """Make authenticated request to Spotify API."""
        await self._ensure_authenticated()

        url = f"{self.config.api_base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = await self.client.request(
                method,
                url,
                params=params,
                json=data,
                headers=headers,
            )

            if response.status_code == 401 and retries < 1:
                # Token expired, try to refresh
                await self._refresh_access_token()
                return await self._make_request(
                    method, endpoint, params, data, retries + 1
                )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise SpotifyAPIError(
                f"API request failed: {e.response.text}",
                status_code=e.response.status_code,
                response=e.response.json() if e.response.content else None,
            ) from e

    async def get_current_user(self) -> User:
        """Get current user information."""
        data = await self._make_request("GET", "/me")
        return User.model_validate(data)

    async def get_user_playlists(
        self, user_id: str | None = None, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get user's playlists."""
        user = user_id or self._user_id or (await self.get_current_user()).id
        params = {"limit": str(limit), "offset": str(offset)}

        data = await self._make_request(
            "GET", f"/users/{user}/playlists", params=params
        )
        return data["items"]

    async def get_playlist(
        self,
        playlist_id: str,
        fields: str | None = None,
        market: str | None = None,
    ) -> Playlist:
        """Get playlist details."""
        params = {}
        if fields:
            params["fields"] = fields
        if market:
            params["market"] = market

        data = await self._make_request(
            "GET", f"/playlists/{playlist_id}", params=params
        )
        return Playlist.model_validate(data)

    async def create_playlist(
        self,
        name: str,
        description: str | None = None,
        public: bool = True,
        collaborative: bool = False,
        user_id: str | None = None,
    ) -> Playlist:
        """Create a new playlist."""
        user = user_id or self._user_id or (await self.get_current_user()).id

        data: dict[str, Any] = {
            "name": name,
            "public": public,
            "collaborative": collaborative,
        }
        if description:
            data["description"] = description

        response_data = await self._make_request(
            "POST", f"/users/{user}/playlists", data=data
        )
        return Playlist.model_validate(response_data)

    async def add_tracks_to_playlist(
        self, playlist_id: str, track_uris: list[str], position: int | None = None
    ) -> str:
        """Add tracks to a playlist."""
        data: dict[str, Any] = {"uris": track_uris}
        if position is not None:
            data["position"] = position

        response_data = await self._make_request(
            "POST", f"/playlists/{playlist_id}/tracks", data=data
        )
        return response_data["snapshot_id"]

    async def remove_tracks_from_playlist(
        self, playlist_id: str, track_uris: list[str], snapshot_id: str | None = None
    ) -> str:
        """Remove tracks from a playlist."""
        data: dict[str, Any] = {"uris": track_uris}
        if snapshot_id:
            data["snapshot_id"] = snapshot_id

        response_data = await self._make_request(
            "DELETE", f"/playlists/{playlist_id}/tracks", data=data
        )
        return response_data["snapshot_id"]

    async def update_playlist(
        self,
        playlist_id: str,
        name: str | None = None,
        description: str | None = None,
        public: bool | None = None,
        collaborative: bool | None = None,
    ) -> None:
        """Update playlist details."""
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if public is not None:
            data["public"] = public
        if collaborative is not None:
            data["collaborative"] = collaborative

        await self._make_request("PUT", f"/playlists/{playlist_id}", data=data)

    async def search(
        self,
        query: str,
        types: list[str] | None = None,
        market: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> SearchResult:
        """Search for tracks, artists, albums, or playlists."""
        params = {
            "q": query,
            "limit": str(limit),
            "offset": str(offset),
        }
        if types:
            params["type"] = ",".join(types)
        if market:
            params["market"] = market

        data = await self._make_request("GET", "/search", params=params)
        return SearchResult.model_validate(data)

    async def search_tracks(
        self, query: str, market: str | None = None, limit: int = 20, offset: int = 0
    ) -> list[Track]:
        """Search for tracks."""
        result = await self.search(query, ["track"], market, limit, offset)
        if result.tracks and "items" in result.tracks:
            return [Track.model_validate(item) for item in result.tracks["items"]]
        return []

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

    async def _ensure_authenticated(self):
        """Ensure we have a valid access token."""
        if not self._access_token:
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

        logger.info("Successfully obtained access token")

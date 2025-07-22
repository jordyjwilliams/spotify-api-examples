"""FastAPI-based authentication server for Spotify OAuth."""

import asyncio
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from .config import SpotifyConfig


class AuthServer:
    """FastAPI server for handling Spotify OAuth callbacks."""

    def __init__(self, config: SpotifyConfig):
        # Extract host and port from redirect URI
        redirect_uri_parsed = urlparse(str(config.redirect_uri))
        self.host = redirect_uri_parsed.hostname or "127.0.0.1"
        self.port = redirect_uri_parsed.port or 8000

        self.app = FastAPI(title="Spotify OAuth Callback")
        self.auth_code: str | None = None
        self.auth_error: str | None = None
        self.state: str | None = None
        self._server_task: asyncio.Task | None = None
        self._server: uvicorn.Server | None = None

        # Setup routes
        self.app.get("/callback")(self.callback_handler)

    async def callback_handler(self, request: Request):
        """Handle the OAuth callback from Spotify."""
        params = dict(request.query_params)

        # Check for errors
        if "error" in params:
            self.auth_error = params["error"]
            return HTMLResponse(
                f"""
                <html>
                <body>
                    <h1>Authorization Error</h1>
                    <p>There was an error during authorization: {self.auth_error}</p>
                    <p>You can close this window and try again.</p>
                </body>
                </html>
                """
            )

        # Verify state
        if "state" in params:
            self.state = params["state"]

        # Get authorization code
        if "code" in params:
            self.auth_code = params["code"]
            return HTMLResponse(
                """
                <html>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You have been successfully authorized.</p>
                    <p>You can close this window and return to your application.</p>
                </body>
                </html>
                """
            )

        return HTMLResponse(
            """
            <html>
            <body>
                <h1>Invalid Callback</h1>
                <p>No authorization code received.</p>
                <p>You can close this window and try again.</p>
            </body>
            </html>
            """
        )

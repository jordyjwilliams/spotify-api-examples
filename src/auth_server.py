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

    async def start(self):
        """Start the FastAPI server."""
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            # Only show critical errors
            # NOTE: If this was `error` error on early exit.
            # This could probably be handled nicer. But for now this works.
            log_level="critical",
            access_log=False,
            loop="asyncio",
        )
        self._server = uvicorn.Server(config)
        self._server_task = asyncio.create_task(self._server.serve())

    async def stop(self):
        """Stop the FastAPI server."""
        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                # This is expected when cancelling the task
                pass
            except Exception as e:
                # Log any other errors but don't raise them
                print(f"Warning: Error stopping auth server: {e}")

    async def wait_for_auth(self, expected_state: str, timeout: int = 300) -> str:
        """Wait for authentication callback and return the authorization code."""
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < timeout:
            if self.auth_error:
                raise Exception(f"Authorization error: {self.auth_error}")

            if self.auth_code and self.state == expected_state:
                return self.auth_code

            await asyncio.sleep(0.1)

        raise Exception("Authentication timeout")

    @asynccontextmanager
    async def serve(self):
        """Context manager for serving the auth server."""
        await self.start()
        try:
            yield self
        finally:
            # Graceful shutdown
            if self._server and hasattr(self._server, "should_exit"):
                self._server.should_exit = True
            # Use a timeout to avoid hanging
            try:
                await asyncio.wait_for(self.stop(), timeout=1.0)
            except TimeoutError:
                # Force cancel if timeout
                if self._server_task:
                    self._server_task.cancel()

"""Track operations for Spotify API."""

from .base_client import BaseSpotifyClient
from .models import Track


class TrackClient:
    """Client for track operations."""

    def __init__(self, base_client: BaseSpotifyClient):
        self._client = base_client

    async def get_track(self, track_id: str) -> Track:
        """Get track details."""
        data = await self._client._make_request("GET", f"/tracks/{track_id}")
        return Track.model_validate(data)

    async def search_tracks(
        self, query: str, market: str | None = None, limit: int = 20, offset: int = 0
    ) -> list[Track]:
        """Search for tracks."""
        result = await self._client.search(query, ["track"], market, limit, offset)
        if result.get("tracks") and "items" in result["tracks"]:
            return [Track.model_validate(item) for item in result["tracks"]["items"]]
        return []

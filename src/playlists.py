"""Playlist operations for Spotify API."""

from typing import Any

from .base_client import BaseSpotifyClient
from .models import Playlist


class PlaylistClient:
    """Client for playlist operations."""

    def __init__(self, base_client: BaseSpotifyClient):
        self._client = base_client

    async def get_user_playlists(
        self, user_id: str | None = None, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get user's playlists."""
        user = (
            user_id
            or self._client._user_id
            or (await self._client.get_current_user()).id
        )
        params = {"limit": str(limit), "offset": str(offset)}

        data = await self._client._make_request(
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

        data = await self._client._make_request(
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
        user = (
            user_id
            or self._client._user_id
            or (await self._client.get_current_user()).id
        )

        data: dict[str, Any] = {
            "name": name,
            "public": public,
            "collaborative": collaborative,
        }
        if description:
            data["description"] = description

        response_data = await self._client._make_request(
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

        response_data = await self._client._make_request(
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

        response_data = await self._client._make_request(
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

        await self._client._make_request("PUT", f"/playlists/{playlist_id}", data=data)

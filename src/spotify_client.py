"""Unified Spotify client that combines all specialized modules."""

from .base_client import BaseSpotifyClient
from .playlists import PlaylistClient
from .tracks import TrackClient


class SpotifyClient(BaseSpotifyClient):
    """Unified Spotify client with all operations."""

    def __init__(self, config=None):
        super().__init__(config)
        self.playlists = PlaylistClient(self)
        self.tracks = TrackClient(self)

    # Convenience methods that delegate to specialized clients
    async def get_user_playlists(self, user_id=None, limit=20, offset=0):
        """Get user's playlists."""
        return await self.playlists.get_user_playlists(user_id, limit, offset)

    async def get_playlist(self, playlist_id, fields=None, market=None):
        """Get playlist details."""
        return await self.playlists.get_playlist(playlist_id, fields, market)

    async def create_playlist(
        self, name, description=None, public=True, collaborative=False, user_id=None
    ):
        """Create a new playlist."""
        return await self.playlists.create_playlist(
            name, description, public, collaborative, user_id
        )

    async def add_tracks_to_playlist(self, playlist_id, track_uris, position=None):
        """Add tracks to a playlist."""
        return await self.playlists.add_tracks_to_playlist(
            playlist_id, track_uris, position
        )

    async def remove_tracks_from_playlist(
        self, playlist_id, track_uris, snapshot_id=None
    ):
        """Remove tracks from a playlist."""
        return await self.playlists.remove_tracks_from_playlist(
            playlist_id, track_uris, snapshot_id
        )

    async def update_playlist(
        self, playlist_id, name=None, description=None, public=None, collaborative=None
    ):
        """Update playlist details."""
        return await self.playlists.update_playlist(
            playlist_id, name, description, public, collaborative
        )

    async def get_track(self, track_id):
        """Get track details."""
        return await self.tracks.get_track(track_id)

    async def search_tracks(self, query, market=None, limit=20, offset=0):
        """Search for tracks."""
        return await self.tracks.search_tracks(query, market, limit, offset)

    async def get_user_country(self):
        """Get user's country."""
        user_data = await self._make_request("GET", "/me")
        return user_data.get("country")

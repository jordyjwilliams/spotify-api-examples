"""Pydantic models for Spotify API data structures."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, HttpUrl, field_validator


class ExternalUrls(BaseModel):
    """External URLs for Spotify objects."""

    spotify: HttpUrl


class Image(BaseModel):
    """Image object for Spotify content."""

    url: HttpUrl
    height: int | None = None
    width: int | None = None


class Followers(BaseModel):
    """Followers information."""

    href: HttpUrl | None = None
    total: int = 0


class User(BaseModel):
    """Spotify user object."""

    id: str
    display_name: str | None = None
    external_urls: ExternalUrls
    followers: Followers | None = None
    href: HttpUrl
    images: list[Image] | None = []
    type: str = "user"
    uri: str

    @field_validator("uri")
    @classmethod
    def validate_uri(cls, v: str) -> str:
        """Validate that URI follows Spotify format."""
        if not v.startswith("spotify:user:"):
            raise ValueError('User URI must start with "spotify:user:"')
        return v


class Artist(BaseModel):
    """Spotify artist object."""

    id: str
    name: str
    external_urls: ExternalUrls
    href: HttpUrl
    images: list[Image] | None = []
    type: str = "artist"
    uri: str

    @field_validator("uri")
    @classmethod
    def validate_uri(cls, v: str) -> str:
        """Validate that URI follows Spotify format."""
        if not v.startswith("spotify:artist:"):
            raise ValueError('Artist URI must start with "spotify:artist:"')
        return v


class Album(BaseModel):
    """Spotify album object."""

    id: str
    name: str
    album_type: str
    artists: list[Artist]
    external_urls: ExternalUrls
    href: HttpUrl
    images: list[Image] | None = []
    release_date: str
    release_date_precision: str
    type: str = "album"
    uri: str

    @field_validator("uri")
    @classmethod
    def validate_uri(cls, v: str) -> str:
        """Validate that URI follows Spotify format."""
        if not v.startswith("spotify:album:"):
            raise ValueError('Album URI must start with "spotify:album:"')
        return v


class Track(BaseModel):
    """Spotify track object."""

    id: str
    name: str
    album: Album
    artists: list[Artist]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: dict[str, str] = {}
    external_urls: ExternalUrls
    href: HttpUrl
    is_local: bool
    is_playable: bool | None = None
    linked_from: Any | None = None
    popularity: int
    preview_url: HttpUrl | None = None
    track_number: int
    type: str = "track"
    uri: str

    @field_validator("uri")
    @classmethod
    def validate_uri(cls, v: str) -> str:
        """Validate that URI follows Spotify format."""
        if not v.startswith("spotify:track:"):
            raise ValueError('Track URI must start with "spotify:track:"')
        return v

    @property
    def duration_seconds(self) -> float:
        """Get track duration in seconds."""
        return self.duration_ms / 1000.0

    @property
    def duration_formatted(self) -> str:
        """Get formatted track duration."""
        total_seconds = int(self.duration_seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"


class PlaylistTrack(BaseModel):
    """Track within a playlist context."""

    added_at: datetime
    added_by: User
    is_local: bool
    primary_color: str | None = None
    track: Track
    video_thumbnail: dict[str, Any] | None = None


class PlaylistTracks(BaseModel):
    """Playlist tracks container."""

    href: HttpUrl
    items: list[PlaylistTrack]
    limit: int
    next: HttpUrl | None = None
    offset: int
    previous: HttpUrl | None = None
    total: int


class Playlist(BaseModel):
    """Spotify playlist object."""

    id: str
    name: str
    collaborative: bool
    description: str | None = None
    external_urls: ExternalUrls
    followers: Followers | None = None
    href: HttpUrl
    images: list[Image] | None = []
    owner: User
    primary_color: str | None = None
    public: bool
    snapshot_id: str
    tracks: PlaylistTracks
    type: str = "playlist"
    uri: str

    @field_validator("uri")
    @classmethod
    def validate_uri(cls, v: str) -> str:
        """Validate that URI follows Spotify format."""
        if not v.startswith("spotify:playlist:"):
            raise ValueError('Playlist URI must start with "spotify:playlist:"')
        return v

    @property
    def track_count(self) -> int:
        """Get number of tracks in playlist."""
        return self.tracks.total

    @property
    def duration_ms(self) -> int:
        """Get total duration in milliseconds."""
        return sum(track.track.duration_ms for track in self.tracks.items)

    @property
    def duration_formatted(self) -> str:
        """Get formatted total duration."""
        total_seconds = self.duration_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def to_simplified(self) -> dict[str, Any]:
        """Convert to simplified playlist for list views."""
        return {
            "id": self.id,
            "name": self.name,
            "collaborative": self.collaborative,
            "description": self.description,
            "external_urls": self.external_urls,
            "href": self.href,
            "images": self.images,
            "owner": self.owner,
            "primary_color": self.primary_color,
            "public": self.public,
            "snapshot_id": self.snapshot_id,
            "tracks": {"total": self.tracks.total, "href": str(self.tracks.href)},
            "type": self.type,
            "uri": self.uri,
        }


class SearchResult(BaseModel):
    """Search result container."""

    tracks: dict[str, Any] | None = None
    artists: dict[str, Any] | None = None
    albums: dict[str, Any] | None = None
    playlists: dict[str, Any] | None = None

"""Pydantic models for Spotify API data structures."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


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


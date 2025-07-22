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


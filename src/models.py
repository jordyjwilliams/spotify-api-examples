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


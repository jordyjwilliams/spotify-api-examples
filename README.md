# Spotify API Examples

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Linting: ruff](https://img.shields.io/badge/linting-ruff-red.svg)](https://github.com/astral-sh/ruff)
[![Type checking: pyright](https://img.shields.io/badge/type%20checking-pyright-yellow.svg)](https://github.com/microsoft/pyright)

Secure examples and tools for working with the [Spotify Web API](https://developer.spotify.com/documentation/web-api) playlists endpoints.

## 🚀 Features

- **Secure credential management** using environment variables and `.env` files
- **Type-safe API interactions** with Pydantic models
- **Modern Python tooling** with uv, ruff, and pyright
- **Comprehensive examples** for all playlist endpoints
- **Token persistence** for seamless authentication
- **Async support** for high-performance operations

## 📋 Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) for package management
- A Spotify Developer account and app credentials

## 🛠️ Installation

1. **Clone the repository:**
2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up your environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Spotify credentials
   ```

### Getting Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add `http://localhost:8888/callback` to your Redirect URIs
4. Copy your Client ID and Client Secret

## 🔐 Authentication & Token Persistence

The library uses Spotify's OAuth 2.0 Authorization Code flow for secure authentication. Here's how it works:

### First-Time Authentication

When you run the library for the first time:

1. **Browser Opens**: A browser window will open to Spotify's authorization page
2. **User Consent**: You'll be asked to authorize the app to access your Spotify account
3. **Token Exchange**: The library exchanges the authorization code for access and refresh tokens
4. **Token Caching**: Tokens are automatically saved to `.spotify_token_cache.json` for future use
    * This happens is this script and tooling here is primarily for local testing.

### Subsequent Runs

On subsequent runs, the library will:

1. **Load Cached Tokens**: Automatically load tokens from the cache file
2. **Validate Tokens**: Test the cached tokens to ensure they're still valid
3. **Use Cached Tokens**: If valid, use them directly without re-authentication
4. **Auto-Refresh**: If access token expires, automatically refresh using the refresh token
5. **Re-authenticate**: Only if tokens are completely invalid (e.g., revoked by user)

### Token Cache Management

```python
from src.spotify import SpotifyClient

async with SpotifyClient() as client:
    # Get user's playlists
    playlists = await client.get_user_playlists()
    
    # Create a new playlist
    playlist = await client.create_playlist(
        name="My Playlist",
        description="A test playlist"
    )
    
    # Add tracks
    await client.add_tracks_to_playlist(
        playlist_id=playlist.id,
        track_ids=["spotify:track:4iV5W9uYEdYUVa79Axb7Rh"]
    )
```

## 📚 Examples

### Basic Playlist Operations

```python
from src.spotify import SpotifyClient

async def main():
    async with SpotifyClient() as client:
        # Get current user's playlists
        playlists = await client.get_user_playlists()
        print(f"Found {len(playlists)} playlists")
        
        # Get a specific playlist
        playlist = await client.get_playlist("37i9dQZF1DXcBWIGoYBM5M")
        print(f"Playlist: {playlist.name}")
        print(f"Tracks: {playlist.tracks.total}")
```

### Creating and Managing Playlists

```python
async def create_playlist_example():
    async with SpotifyClient() as client:
        # Create a new playlist
        playlist = await client.create_playlist(
            name="My Awesome Playlist",
            description="Created with Spotify API",
            public=False
        )
        
        # Add tracks by search
        tracks = await client.search_tracks("artist:Queen")
        track_uris = [track.uri for track in tracks[:5]]
        
        await client.add_tracks_to_playlist(playlist.id, track_uris)
        print(f"Added {len(track_uris)} tracks to {playlist.name}")
```
## 🔧 Development

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run pyright

# Run all checks
uv run ruff check . && uv run ruff format --check . && uv run pyright
```
## 🏗️ Project Structure

```
spotify-api-examples/
├── src/
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── config.py           # Configuration management
│   ├── models.py           # Pydantic models
│   ├── spotify.py          # Main Spotify client
│   └── utils.py            # Utility functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Test configuration
│   ├── test_playlists.py   # Playlist tests
│   └── test_spotify.py     # Client tests
├── .env.example            # Environment template
├── .gitignore
├── pyproject.toml          # Project configuration
├── README.md
└── LICENSE
```

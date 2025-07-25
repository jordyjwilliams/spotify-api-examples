# Spotify API Examples

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/jordywilliams/spotify-api-examples/check.yaml?branch=main)](https://github.com/jordywilliams/spotify-api-examples/actions)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Linting: ruff](https://img.shields.io/badge/linting-ruff-red.svg)](https://github.com/astral-sh/ruff)
[![Type checking: pyright](https://img.shields.io/badge/type%20checking-pyright-yellow.svg)](https://github.com/microsoft/pyright)

Secure examples and tools for working with the [Spotify Web API](https://developer.spotify.com/documentation/web-api) playlists endpoints.

## 🚀 Features

- **Modular architecture** with specialized clients for different API domains
- **Secure credential management** using environment variables and `.env` files
- **Type-safe API interactions** with Pydantic models
- **Modern Python tooling** with uv, ruff, and pyright
- **Comprehensive examples** for all playlist endpoints
- **Token persistence** for seamless authentication
- **Async support** for high-performance operations
- **Extensible design** for easy addition of new API endpoints

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
from src.spotify_client import SpotifyClient

# Clear the authentication cache (forces re-authentication)
client = SpotifyClient()
client.clear_auth_cache()
```

## 📚 Examples

## 🎯 Quick Start

The easiest way to get started is with the comprehensive example script:

```bash
uv run python -m examples.basic_usage
```

**What it demonstrates:**
- User authentication and profile retrieval
- Playlist management (create, read, update)
- Track search and discovery
- Playlist modification (adding tracks)
> [!TIP]
> **Quick Start**: The `basic_usage.py` script is the best way to get started! It provides a complete demonstration of all the library's features with beautiful console output using Rich. Run it after setting up your `.env` file to see everything in action.
> 
> **Token Persistence**: Authentication tokens are automatically cached in `.spotify_token_cache.json` and will be reused on subsequent runs, so you won't need to re-authenticate each time!

> [!IMPORTANT]
> This will create playlists in your account!

## 🏗️ Architecture

The library uses a modular architecture for better separation of concerns and extensibility:

### Core Components

- **`BaseSpotifyClient`**: Handles authentication, HTTP requests, and token management
- **`PlaylistClient`**: Specialized client for playlist operations
- **`TrackClient`**: Specialized client for track operations
- **`SpotifyClient`**: Unified client that combines all specialized clients

### Usage Patterns

**Option 1: Unified Client (Recommended)**
```python
from src.spotify_client import SpotifyClient

async with SpotifyClient() as client:
    playlists = await client.get_user_playlists()
    tracks = await client.search_tracks("query")
```

**Option 2: Direct Module Usage**
```python
from src.base_client import BaseSpotifyClient
from src.playlists import PlaylistClient
from src.tracks import TrackClient

async with BaseSpotifyClient() as base_client:
    playlists = PlaylistClient(base_client)
    tracks = TrackClient(base_client)
    
    user_playlists = await playlists.get_user_playlists()
    search_results = await tracks.search_tracks("query")
```

### Benefits of Modular Architecture

- **Separation of Concerns**: Each module has a single responsibility
- **Easier Testing**: Test each module independently
- **Better Maintainability**: Changes to playlist logic don't affect track logic
- **Extensibility**: Easy to add new modules (e.g., `albums.py`, `artists.py`)
- **Code Reuse**: Base client can be used by other projects
- **Cleaner Imports**: Import only what you need

### Basic Playlist Operations

```python
from src.spotify_client import SpotifyClient

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

### Search and Discovery

```python
async def search_example():
    async with SpotifyClient() as client:
        # Search for tracks
        tracks = await client.search_tracks("artist:Queen", limit=10)
        
        # Search for playlists
        results = await client.search("workout", ["playlist"], limit=5)
        playlists = results.playlists.items if results.playlists else []
        
        print(f"Found {len(tracks)} tracks and {len(playlists)} playlists")
```

### Error Handling

```python
from src.spotify_client import SpotifyClient
from src.base_client import SpotifyAPIError

async def error_handling_example():
    async with SpotifyClient() as client:
        try:
            playlist = await client.get_playlist("invalid_playlist_id")
        except SpotifyAPIError as e:
            print(f"API Error: {e}")
            print(f"Status Code: {e.status_code}")
        except Exception as e:
            print(f"Unexpected error: {e}")
```
## 🔧 Development

### Code Quality

```bash
# Format: code/imports
uv run ruff format .
uv run ruff check --select I .

# Lint: code
uv run ruff check .

# Type checking
uv run pyright

# Run all checks
uv run ruff check . && uv run ruff format --check . && uv run pyright

### Testing

The project includes a comprehensive test suite with **73+ tests** covering all major functionality:

```bash
# Run all tests
uv run pytest tests/

# Run tests with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run specific test files
uv run pytest tests/test_core.py -v
uv run pytest tests/test_models.py -v

# Run tests with detailed output
uv run pytest tests/ -v --tb=short
```
## 🏗️ Project Structure

```
spotify-api-examples/
├── src/
│   ├── __init__.py
│   ├── base_client.py      # Base client with auth and HTTP
│   ├── config.py           # Configuration management
│   ├── models.py           # Pydantic models
│   ├── playlists.py        # Playlist operations
│   ├── tracks.py           # Track operations
│   ├── spotify_client.py   # Unified client
│   └── auth_server.py      # OAuth callback server
├── tests/
│   ├── test_config.py      # Configuration validation
│   ├── test_core.py        # Core functionality tests
│   ├── test_models.py      # Pydantic model tests
│   ├── test_playlists.py   # Playlist operations
│   └── test_tracks.py      # Track operations
├── examples/
│   └── basic_usage.py      # Comprehensive example
├── .env.example            # Environment template
├── .gitignore
├── pyproject.toml          # Project configuration
├── README.md
└── LICENSE
```

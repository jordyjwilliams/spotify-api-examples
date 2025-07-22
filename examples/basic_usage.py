#!/usr/bin/env python3
"""Basic usage example for Spotify API client.
NOTE: This will generate playlists in your account!
"""

import asyncio
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import from the src package
from src.spotify import SpotifyAPIError, SpotifyAuthError, SpotifyClient

console = Console()


async def get_user_info(client: SpotifyClient):
    """Get and display current user information."""
    console.print("\n[bold cyan]1. Getting current user...[/bold cyan]")
    user = await client.get_current_user()
    console.print(f"   👋 Welcome, [bold green]{user.display_name}[/bold green]!")
    console.print(f"   🆔 User ID: [dim]{user.id}[/dim]")
    return user


async def display_user_playlists(client: SpotifyClient):
    """Display user's playlists in a formatted table."""
    console.print("\n[bold cyan]2. Fetching your playlists...[/bold cyan]")
    playlists = await client.get_user_playlists(limit=10)
    console.print(f"   📚 Found [bold yellow]{len(playlists)}[/bold yellow] playlists:")

    # Create a table for playlists
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", width=30)
    table.add_column("Tracks", style="yellow", justify="center")
    table.add_column("Public", style="green", justify="center")
    table.add_column("ID", style="dim", width=22)

    for playlist_data in playlists[:5]:  # Show first 5
        tracks_count = playlist_data.get("tracks", {}).get("total", 0)
        is_public = "✓" if playlist_data.get("public", False) else "✗"
        table.add_row(
            playlist_data.get("name", "Unknown"),
            str(tracks_count),
            is_public,
            playlist_data.get("id", "Unknown")
        )

    console.print(table)
    if len(playlists) > 5:
        console.print(f"   [dim]... and {len(playlists) - 5} more playlists (showing top 5)[/dim]")
    return playlists


async def search_and_display_tracks(client: SpotifyClient):
    """Search for tracks and display results in a table."""
    console.print("\n[bold cyan]3. Searching for tracks...[/bold cyan]")
    search_query = "artist:Queen"
    tracks = await client.search_tracks(search_query, limit=5)
    console.print(f"   🔍 Found [bold yellow]{len(tracks)}[/bold yellow] tracks for '[italic]{search_query}[/italic]':")

    # Create a table for tracks
    track_table = Table(show_header=True, header_style="bold magenta")
    track_table.add_column("Title", style="cyan", width=25)
    track_table.add_column("Artist", style="blue", width=20)
    track_table.add_column("Album", style="green", width=25)
    track_table.add_column("Duration", style="yellow", justify="center")

    for track in tracks:
        artists = ", ".join(artist.name for artist in track.artists)
        track_table.add_row(
            track.name,
            artists,
            track.album.name,
            track.duration_formatted
        )

    console.print(track_table)
    return tracks


async def create_test_playlist(client: SpotifyClient):
    """Create a new test playlist."""
    console.print("\n[bold cyan]4. Creating a new playlist...[/bold cyan]")
    playlist_name = "API Test Playlist"
    playlist = await client.create_playlist(
        name=playlist_name,
        description="Created with Spotify API examples",
        public=False,
    )
    console.print(f"   ✅ Created playlist: [bold green]{playlist.name}[/bold green]")
    console.print(f"   🆔 Playlist ID: [dim]{playlist.id}[/dim]")
    console.print(f"   🔗 URL: [link={playlist.external_urls.spotify}]{playlist.external_urls.spotify}[/link]")
    return playlist


async def add_tracks_to_playlist(client: SpotifyClient, playlist, tracks):
    """Add tracks to the specified playlist."""
    if not tracks:
        console.print("\n[bold yellow]⚠️  No tracks to add to playlist[/bold yellow]")
        return None

    console.print("\n[bold cyan]5. Adding tracks to the playlist...[/bold cyan]")
    track_uris = [track.uri for track in tracks[:3]]  # Add first 3 tracks
    snapshot_id = await client.add_tracks_to_playlist(playlist.id, track_uris)
    console.print(f"   ➕ Added [bold yellow]{len(track_uris)}[/bold yellow] tracks to playlist")
    console.print(f"   📸 Snapshot ID: [dim]{snapshot_id}[/dim]")
    return snapshot_id



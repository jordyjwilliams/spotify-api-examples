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


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

#!/usr/bin/env python3
"""Basic usage example for Spotify API client.

This example demonstrates:
1. Getting current user (`get_user_info`)
2. Listing user's playlists (`display_user_playlists`)
3. Searching for tracks (`search_and_display_tracks`)
4. Create a playlist (`create_test_playlist`)
5. Add tracks to a playlist (`add_tracks_to_playlist`)
6. Display updated playlist (`display_updated_playlist`)
7. Track Info (`display_track_info`)

Before running this script, make sure to:
1. Set up your Spotify API credentials in a .env file
2. Install dependencies: uv sync

NOTE: This will generate playlists in your account!
"""

import asyncio
from pathlib import Path
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.base_client import SpotifyAPIError, SpotifyAuthError

# Import from the src package
from src.spotify_client import SpotifyClient

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
            playlist_data.get("id", "Unknown"),
        )

    console.print(table)
    if len(playlists) > 5:
        console.print(
            f"   [dim]... and {len(playlists) - 5} more playlists (showing top 5)[/dim]"
        )
    return playlists


async def search_and_display_tracks(client: SpotifyClient):
    """Search for tracks and display results in a table."""
    console.print("\n[bold cyan]3. Searching for tracks...[/bold cyan]")
    search_query = "artist:Queen"
    tracks = await client.search_tracks(search_query, limit=5)
    console.print(
        f"   🔍 Found [bold yellow]{len(tracks)}[/bold yellow] tracks for '[italic]{search_query}[/italic]':"
    )

    # Create a table for tracks
    track_table = Table(show_header=True, header_style="bold magenta")
    track_table.add_column("Title", style="cyan", width=25)
    track_table.add_column("Artist", style="blue", width=20)
    track_table.add_column("Album", style="green", width=25)
    track_table.add_column("Duration", style="yellow", justify="center")

    for track in tracks:
        artists = ", ".join(artist.name for artist in track.artists)
        track_table.add_row(
            track.name, artists, track.album.name, track.duration_formatted
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
    console.print(
        f"   🔗 URL: [link={playlist.external_urls.spotify}]{playlist.external_urls.spotify}[/link]"
    )
    return playlist


async def add_tracks_to_playlist(client: SpotifyClient, playlist, tracks):
    """Add tracks to the specified playlist."""
    if not tracks:
        console.print("\n[bold yellow]⚠️  No tracks to add to playlist[/bold yellow]")
        return None

    console.print("\n[bold cyan]5. Adding tracks to the playlist...[/bold cyan]")
    track_uris = [track.uri for track in tracks[:3]]  # Add first 3 tracks
    snapshot_id = await client.add_tracks_to_playlist(playlist.id, track_uris)
    console.print(
        f"   ➕ Added [bold yellow]{len(track_uris)}[/bold yellow] tracks to playlist"
    )
    console.print(f"   📸 Snapshot ID: [dim]{snapshot_id}[/dim]")
    return snapshot_id


async def display_updated_playlist(client: SpotifyClient, playlist):
    """Display the updated playlist information."""
    console.print("\n[bold cyan]6. Getting updated playlist...[/bold cyan]")
    updated_playlist = await client.get_playlist(playlist.id)
    console.print(
        f"   📊 Playlist now has [bold yellow]{updated_playlist.track_count}[/bold yellow] tracks"
    )
    console.print(
        f"   ⏱️  Total duration: [bold yellow]{updated_playlist.duration_formatted}[/bold yellow]"
    )
    return updated_playlist


def display_track_info(track):
    """Display track information."""
    console.print("\n[bold cyan]7. Getting Track Info...[/bold cyan]")
    table = Table(
        show_header=True, header_style="bold green", title="Track Information"
    )
    table.add_column("Property", style="cyan", width=20)
    table.add_column("Value", style="yellow", width=40)

    # Basic track information
    table.add_row("Name", track.name)
    table.add_row("Artists", ", ".join(artist.name for artist in track.artists))
    table.add_row("Album", track.album.name)
    table.add_row(
        "Duration",
        f"{track.duration_ms // 1000 // 60}:{track.duration_ms // 1000 % 60:02d}",
    )
    table.add_row("Popularity", f"{track.popularity}/100")
    table.add_row("Explicit", "Yes" if track.explicit else "No")
    table.add_row("Track Number", str(track.track_number))
    table.add_row("Disc Number", str(track.disc_number))

    console.print(table)

    console.print(
        "\n   [dim]💡 Tip: Audio features endpoint is depricated. Track Information:[/dim]"
    )
    console.print(
        "   [dim]   • Track metadata (duration, popularity, explicit content)[/dim]"
    )
    console.print("   [dim]   • Album information[/dim]")
    console.print("   [dim]   • Artist details[/dim]")
    console.print("   [dim]   • Playlist analysis[/dim]")


def display_success():
    """Display success message."""
    console.print(
        Panel.fit(
            "[bold green]✅ Example completed successfully![/bold green]\n[dim]All operations completed without errors.[/dim]",
            border_style="green",
        )
    )


def display_error(error_type: str, error_message: str, additional_info: str = ""):
    """Display formatted error message."""
    console.print(
        Panel.fit(
            f"[bold red]❌ {error_type}[/bold red]\n[red]{error_message}[/red]\n\n[dim]{additional_info}[/dim]",
            border_style="red",
        )
    )


async def main():
    """Main example function."""
    # Header
    console.print(
        Panel.fit(
            "[bold blue]🎵 Spotify API Examples[/bold blue]\n[dim]Basic Usage Demo[/dim]",
            border_style="blue",
        )
    )

    try:
        async with SpotifyClient() as client:
            # Execute all operations
            await get_user_info(client)
            await display_user_playlists(client)
            tracks = await search_and_display_tracks(client)
            playlist = await create_test_playlist(client)
            await add_tracks_to_playlist(client, playlist, tracks)
            await display_updated_playlist(client, playlist)
            # NOTE: for now just display the first track's info
            display_track_info(tracks[0])

            # Success message
            display_success()

    except SpotifyAuthError as e:
        display_error(
            "Authentication Error",
            str(e),
            "Make sure your .env file contains valid Spotify credentials.",
        )
        sys.exit(1)
    except SpotifyAPIError as e:
        display_error("API Error", str(e))
        sys.exit(1)
    except Exception as e:
        display_error("Unexpected Error", str(e))
        sys.exit(1)


if __name__ == "__main__":
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        console.print(
            Panel.fit(
                "[bold red]❌ .env file not found![/bold red]\n\n[dim]Please copy env.example to .env and add your Spotify credentials.[/dim]",
                border_style="red",
            )
        )
        sys.exit(1)

    # Run the example
    asyncio.run(main())

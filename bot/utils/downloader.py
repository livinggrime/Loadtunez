import os
import requests
import subprocess
import json
import re
import io
import tempfile
from bot.config import HIGH_QUALITY, MAX_RETRIES, SPOTIFY_QUALITY, YOUTUBE_QUALITY

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_spotify_track(track_id, output_path=None):
    """Stream a Spotify track directly to memory using yt-dlp."""
    try:
        # Get track info from Spotify API
        from spotipy import Spotify
        from spotipy.oauth2 import SpotifyClientCredentials
        from bot.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
        
        sp = Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))
        
        track = sp.track(track_id)
        track_name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        search_query = f"{artists} - {track_name} audio"
        
        print(f"Searching YouTube for: {search_query}")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name
        
        # Use yt-dlp to search YouTube and download the first result
        subprocess.run([
            'yt-dlp',
            'ytsearch1:' + search_query,
            '-x',  # Extract audio
            '--audio-format', 'mp3',
            '--max-filesize', '45M',  # Limit file size for Telegram
            '--audio-quality', '128K',  # Lower quality for smaller file size
            '-o', temp_path,
            '--no-warnings'
        ], check=True)
        
        # Check if file was downloaded
        if os.path.exists(temp_path):
            # Return the file path and metadata
            return {
                "success": True,
                "path": temp_path,
                "title": track_name,
                "artist": artists,
                "is_temp": True
            }
        else:
            return {
                "success": False,
                "error": "File not found after download attempt"
            }
    except Exception as e:
        print(f"Error downloading Spotify track: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
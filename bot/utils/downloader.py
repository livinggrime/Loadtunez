import os
import requests
import subprocess
import json
import re
from bot.config import HIGH_QUALITY, MAX_RETRIES, SPOTIFY_QUALITY, YOUTUBE_QUALITY

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_file(url, destination, max_retries=MAX_RETRIES):
    """Download a file from a URL to a destination path."""
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(destination, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                return True
            else:
                retries += 1
        except Exception as e:
            print(f"Download error: {str(e)}")
            retries += 1
    
    return False

def download_spotify_track(track_id, output_path):
    """Download a Spotify track using yt-dlp after searching for it."""
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
        
        # Create a safe filename
        safe_filename = "".join([c for c in f"{artists} - {track_name}" if c.isalpha() or c.isdigit() or c in ' -_.']).strip()
        safe_output_path = os.path.join(os.path.dirname(output_path), f"{safe_filename}.mp3")
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(safe_output_path), exist_ok=True)
        
        print(f"Searching YouTube for: {search_query}")
        
        # Use yt-dlp to search YouTube and download the first result
        # Limit file size to 45MB (Telegram limit is 50MB)
        subprocess.run([
            'yt-dlp',
            'ytsearch1:' + search_query,
            '-x',  # Extract audio
            '--audio-format', 'mp3',
            '--max-filesize', '45M',  # Limit file size for Telegram
            '--audio-quality', '192K',  # Lower quality for smaller file size
            '-o', safe_output_path,
            '--no-warnings'
        ], check=True)
        
        # Check if file was downloaded
        if os.path.exists(safe_output_path):
            # Make sure the file has read permissions for everyone
            os.chmod(safe_output_path, 0o644)
            return {
                "success": True,
                "path": safe_output_path
            }
        else:
            # yt-dlp might have saved with a different filename
            base_path = os.path.splitext(safe_output_path)[0]
            if os.path.exists(base_path + '.mp3'):
                # Make sure the file has read permissions for everyone
                os.chmod(base_path + '.mp3', 0o644)
                return {
                    "success": True,
                    "path": base_path + '.mp3'
                }
                
            # Check for other possible extensions
            for ext in ['.webm', '.m4a', '.opus']:
                if os.path.exists(base_path + ext):
                    # Make sure the file has read permissions for everyone
                    os.chmod(base_path + ext, 0o644)
                    return {
                        "success": True,
                        "path": base_path + ext
                    }
                    
            # Look for any file in the directory that was recently created
            dir_path = os.path.dirname(safe_output_path)
            files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
            if files:
                # Get the most recently created file
                newest_file = max(files, key=lambda f: os.path.getctime(os.path.join(dir_path, f)))
                newest_path = os.path.join(dir_path, newest_file)
                # Make sure the file has read permissions for everyone
                os.chmod(newest_path, 0o644)
                return {
                    "success": True,
                    "path": newest_path
                }
                
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

def download_tiktok_video(video_url, output_path):
    """Download a TikTok video using yt-dlp."""
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"Downloading TikTok video from {video_url} to {output_path}")
        
        # Use yt-dlp to download TikTok videos
        subprocess.run([
            'yt-dlp',
            '-o', output_path,
            '--no-warnings',
            video_url
        ], check=True)
        
        # Check if file was downloaded
        if os.path.exists(output_path):
            # Set proper permissions
            os.chmod(output_path, 0o644)
            return {
                "success": True,
                "path": output_path
            }
        else:
            # yt-dlp might have added an extension
            base_path = os.path.splitext(output_path)[0]
            for ext in ['.mp4', '.webm', '.mkv']:
                if os.path.exists(base_path + ext):
                    # Set proper permissions
                    os.chmod(base_path + ext, 0o644)
                    return {
                        "success": True,
                        "path": base_path + ext
                    }
            return {
                "success": False,
                "error": "File not found after download attempt"
            }
    except Exception as e:
        print(f"Error downloading TikTok video: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def download_youtube_video(video_url, output_path):
    """Download a YouTube video using yt-dlp."""
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"Downloading YouTube video from {video_url} to {output_path}")
        
        # Get video info first
        result = subprocess.run([
            'yt-dlp',
            '--dump-json',
            video_url
        ], capture_output=True, text=True, check=True)
        
        video_info = json.loads(result.stdout)
        title = video_info.get('title', 'Unknown Title')
        uploader = video_info.get('uploader', 'Unknown Uploader')
        duration = video_info.get('duration', 0)
        
        # Download the video with size limit
        subprocess.run([
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4][filesize<45M]+bestaudio[ext=m4a][filesize<10M]/best[ext=mp4][filesize<45M]/best[filesize<45M]',
            '-o', output_path,
            video_url
        ], check=True)
        
        # Check if file was downloaded
        if os.path.exists(output_path):
            # Set proper permissions
            os.chmod(output_path, 0o644)
            return {
                "title": title,
                "uploader": uploader,
                "duration": duration,
                "success": True,
                "path": output_path
            }
        else:
            # yt-dlp might have added an extension
            base_path = os.path.splitext(output_path)[0]
            for ext in ['.mp4', '.webm', '.mkv']:
                if os.path.exists(base_path + ext):
                    # Set proper permissions
                    os.chmod(base_path + ext, 0o644)
                    return {
                        "title": title,
                        "uploader": uploader,
                        "duration": duration,
                        "success": True,
                        "path": base_path + ext
                    }
            return {
                "success": False,
                "error": "File not found after download attempt"
            }
    except Exception as e:
        print(f"Error downloading YouTube video: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def download_instagram_reel(reel_url, output_path):
    """Download an Instagram reel using yt-dlp."""
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"Downloading Instagram reel from {reel_url} to {output_path}")
        
        # Extract the shortcode from the URL
        match = re.search(r'instagram\.com/(reel|p)/([^/?]+)', reel_url)
        if not match:
            return {
                "success": False,
                "error": "Invalid Instagram URL"
            }
        
        shortcode = match.group(2)
        
        # Use yt-dlp for Instagram as well (it works for reels and posts)
        subprocess.run([
            'yt-dlp',
            '-o', output_path,
            '--max-filesize', '45M',  # Limit file size for Telegram
            '--no-warnings',
            reel_url
        ], check=True)
        
        # Check if file was downloaded
        if os.path.exists(output_path):
            # Set proper permissions
            os.chmod(output_path, 0o644)
            return {
                "success": True,
                "path": output_path
            }
        else:
            # yt-dlp might have added an extension
            base_path = os.path.splitext(output_path)[0]
            for ext in ['.mp4', '.jpg', '.png']:
                if os.path.exists(base_path + ext):
                    # Set proper permissions
                    os.chmod(base_path + ext, 0o644)
                    return {
                        "success": True,
                        "path": base_path + ext
                    }
            return {
                "success": False,
                "error": "File not found after download attempt"
            }
    except Exception as e:
        print(f"Error downloading Instagram reel: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
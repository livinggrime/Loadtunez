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
    """Download a Spotify track using spotdl."""
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Construct the Spotify URL
        spotify_url = f"https://open.spotify.com/track/{track_id}"
        
        # Use spotdl to download the track
        output_dir = os.path.dirname(output_path)
        filename = os.path.basename(output_path)
        
        print(f"Downloading Spotify track {track_id} to {output_path}")
        
        subprocess.run([
            'spotdl', 
            'download', 
            spotify_url, 
            '--output', 
            f'{output_dir}/{filename}'
        ], check=True)
        
        # Check if file was downloaded
        if os.path.exists(output_path):
            return {
                "success": True,
                "path": output_path
            }
        else:
            # spotdl might have saved with a different filename, try to find it
            files = os.listdir(output_dir)
            if files:
                # Get the most recently created file
                newest_file = max(files, key=lambda f: os.path.getctime(os.path.join(output_dir, f)))
                newest_path = os.path.join(output_dir, newest_file)
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
    """Download a TikTok video using youtube-dl."""
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"Downloading TikTok video from {video_url} to {output_path}")
        
        # Use youtube-dl to download TikTok videos
        subprocess.run([
            'youtube-dl',
            '-o', output_path,
            '--no-warnings',
            video_url
        ], check=True)
        
        # Check if file was downloaded
        if os.path.exists(output_path):
            return {
                "success": True,
                "path": output_path
            }
        else:
            # youtube-dl might have added an extension
            base_path = os.path.splitext(output_path)[0]
            for ext in ['.mp4', '.webm', '.mkv']:
                if os.path.exists(base_path + ext):
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
    """Download a YouTube video using youtube-dl."""
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"Downloading YouTube video from {video_url} to {output_path}")
        
        # Get video info first
        result = subprocess.run([
            'youtube-dl',
            '--dump-json',
            video_url
        ], capture_output=True, text=True, check=True)
        
        video_info = json.loads(result.stdout)
        title = video_info.get('title', 'Unknown Title')
        uploader = video_info.get('uploader', 'Unknown Uploader')
        duration = video_info.get('duration', 0)
        
        # Download the video
        subprocess.run([
            'youtube-dl',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '-o', output_path,
            video_url
        ], check=True)
        
        # Check if file was downloaded
        if os.path.exists(output_path):
            return {
                "title": title,
                "uploader": uploader,
                "duration": duration,
                "success": True,
                "path": output_path
            }
        else:
            # youtube-dl might have added an extension
            base_path = os.path.splitext(output_path)[0]
            for ext in ['.mp4', '.webm', '.mkv']:
                if os.path.exists(base_path + ext):
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
    """Download an Instagram reel using instaloader."""
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
        
        # Use youtube-dl for Instagram as well (it works for reels and posts)
        subprocess.run([
            'youtube-dl',
            '-o', output_path,
            '--no-warnings',
            reel_url
        ], check=True)
        
        # Check if file was downloaded
        if os.path.exists(output_path):
            return {
                "success": True,
                "path": output_path
            }
        else:
            # youtube-dl might have added an extension
            base_path = os.path.splitext(output_path)[0]
            for ext in ['.mp4', '.jpg', '.png']:
                if os.path.exists(base_path + ext):
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
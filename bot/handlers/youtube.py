import re
import os
import glob
from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.downloader import download_youtube_video, ensure_directory_exists

def extract_youtube_id(url):
    """Extract YouTube video ID from URL."""
    # Standard YouTube URL
    match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    
    # Shortened YouTube URL
    match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    
    return None

def handle_youtube_url(update: Update, context: CallbackContext):
    url = update.message.text
    DOWNLOAD_DIRECTORY = os.environ.get("DOWNLOAD_DIRECTORY", "/tmp")
    # Use yt-dlp to download as mp3
    output_path = os.path.join(DOWNLOAD_DIRECTORY, "%(title)s.%(ext)s")
    cmd = f'yt-dlp -x --audio-format mp3 -o "{output_path}" "{url}"'
    os.system(cmd)
    # Find the newest mp3 file in the directory
    mp3_files = glob.glob(os.path.join(DOWNLOAD_DIRECTORY, "*.mp3"))
    if not mp3_files:
        update.message.reply_text("Download failed. No audio file found.")
        return
    latest_file = max(mp3_files, key=os.path.getctime)
    print(f"Downloaded: {latest_file}, Size: {os.path.getsize(latest_file)} bytes")  # Debug print
    with open(latest_file, "rb") as f:
        update.message.reply_audio(f, filename=os.path.basename(latest_file))
    os.remove(latest_file)
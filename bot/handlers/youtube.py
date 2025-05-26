import re
import os
from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.downloader import download_youtube_video, ensure_directory_exists
from bot.config import DOWNLOAD_DIRECTORY

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

def handle_youtube_url(update: Update, context: CallbackContext) -> None:
    """Handle YouTube URLs."""
    url = update.message.text
    video_id = extract_youtube_id(url)
    
    if not video_id:
        update.message.reply_text("Invalid YouTube URL. Please provide a valid YouTube video link.")
        return
    
    update.message.reply_text("🎬 Processing YouTube video...")
    
    try:
        # Ensure download directory exists
        ensure_directory_exists(DOWNLOAD_DIRECTORY)
        
        # Download the video
        output_path = os.path.join(DOWNLOAD_DIRECTORY, f"youtube_{video_id}.mp4")
        
        # In a real implementation, this would use youtube-dl or a similar library
        # to download the video with the highest quality
        update.message.reply_text("Downloading video in high quality... This may take a while.")
        
        # Download the video
        video_info = download_youtube_video(url, output_path)
        
        if video_info and os.path.exists(output_path):
            update.message.reply_text(f"✅ Downloaded: *{video_info.get('title', 'YouTube Video')}*", parse_mode='Markdown')
            
            # Send the video file if it's not too large
            file_size = os.path.getsize(output_path)
            if file_size < 50 * 1024 * 1024:  # Telegram bot API limit is 50MB
                with open(output_path, 'rb') as video_file:
                    update.message.reply_video(
                        video=video_file,
                        caption=f"Title: {video_info.get('title', 'YouTube Video')}\nChannel: {video_info.get('uploader', 'Unknown')}"
                    )
            else:
                update.message.reply_text(
                    f"The video is too large to send via Telegram (size: {file_size / (1024 * 1024):.1f} MB).\n"
                    f"You can find it at: {output_path}"
                )
        else:
            update.message.reply_text("❌ Failed to download the video.")
            
    except Exception as e:
        update.message.reply_text(f"❌ Error downloading YouTube video: {str(e)}")
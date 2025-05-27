import re
import os
from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.downloader import ensure_directory_exists
from bot.config import DOWNLOAD_DIRECTORY

def extract_instagram_id(url):
    """Extract Instagram reel or post ID from URL."""
    # Reel pattern
    match = re.search(r'instagram\.com/reel/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1), 'reel'
    
    # Post pattern
    match = re.search(r'instagram\.com/p/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1), 'post'
    
    return None, None

def handle_instagram_url(update: Update, context: CallbackContext) -> None:
    """Handle Instagram URLs."""
    url = update.message.text
    content_id, content_type = extract_instagram_id(url)
    
    if not content_id:
        update.message.reply_text("Invalid Instagram URL. Please provide a valid Instagram reel or post link.")
        return
    
    update.message.reply_text(f"📸 Processing Instagram {content_type}...")
    
    try:
        # Ensure download directory exists
        ensure_directory_exists(DOWNLOAD_DIRECTORY)
        
        # Download the content
        output_path = os.path.join(DOWNLOAD_DIRECTORY, f"instagram_{content_id}.mp4")
        
        # In a real implementation, this would use instaloader or a similar library
        # to download the reel or post
        update.message.reply_text(f"Downloading Instagram {content_type}... This may take a while.")
        
        # Download the content
        # In a real implementation, you would use a library like instaloader
        # or a service that can download Instagram content
        
        # For demonstration purposes
        update.message.reply_text(
            "In a real implementation, the Instagram content would be downloaded and sent here.\n\n"
            "To implement this fully, you would need to:\n"
            "1. Use an Instagram downloader library like instaloader\n"
            "2. Handle authentication if required\n"
            "3. Download the reel or post\n"
            "4. Send the media file to the user"
        )
        
        # Example of how the real implementation would look:
        # content_info = download_instagram_reel(url, output_path)
        # 
        # if os.path.exists(output_path):
        #     update.message.reply_text(f"✅ Downloaded Instagram {content_type} successfully!")
        #     
        #     with open(output_path, 'rb') as media_file:
        #         if content_type == 'reel' or output_path.endswith('.mp4'):
        #             update.message.reply_video(
        #                 video=media_file,
        #                 caption=f"Downloaded from Instagram"
        #             )
        #         else:
        #             update.message.reply_photo(
        #                 photo=media_file,
        #                 caption=f"Downloaded from Instagram"
        #             )
        # else:
        #     update.message.reply_text(f"❌ Failed to download the Instagram {content_type}.")
        
    except Exception as e:
        update.message.reply_text(f"❌ Error downloading Instagram {content_type}: {str(e)}")
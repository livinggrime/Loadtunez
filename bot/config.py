import os

# Bot configuration
API_TOKEN = os.getenv('API_TOKEN', 'YOUR_TELEGRAM_BOT_API_TOKEN')

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', 'YOUR_SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'YOUR_SPOTIFY_CLIENT_SECRET')

# TikTok API credentials (if using a third-party API)
TIKTOK_API_KEY = os.getenv('TIKTOK_API_KEY', 'YOUR_TIKTOK_API_KEY')

# YouTube API credentials (optional, youtube-dl doesn't require API keys)
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'YOUR_YOUTUBE_API_KEY')

# Instagram credentials (if using a library that requires authentication)
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', 'YOUR_INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', 'YOUR_INSTAGRAM_PASSWORD')

# Download settings
DOWNLOAD_DIRECTORY = os.getenv('DOWNLOAD_DIRECTORY', 'downloads/')
HIGH_QUALITY = os.getenv('HIGH_QUALITY', 'True').lower() == 'true'
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024  # 50MB - Telegram bot API limit

# Spotify download settings
SPOTIFY_QUALITY = 320  # kbps

# YouTube download settings
YOUTUBE_QUALITY = 'best'  # Options: best, 1080p, 720p, etc.

# User rate limiting (to prevent abuse)
MAX_DOWNLOADS_PER_DAY = 50
MAX_DOWNLOADS_PER_HOUR = 10
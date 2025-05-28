# Loadtunez

A Telegram bot for downloading music and videos from various platforms.

## Requirements

- Python 3.8+
- FFmpeg (required for audio conversion)
- Telegram Bot API token
- Spotify API credentials

## Installation

1. Install FFmpeg:
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env` file:
   ```
   API_TOKEN=your_telegram_bot_token
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   DOWNLOAD_DIRECTORY=/path/to/downloads
   ```

## Running the Bot

```
python main.py
```

## Features

- Download tracks from Spotify
- Convert YouTube videos to MP3
- Download TikTok videos (placeholder)
- Download Instagram reels and posts (placeholder)
# Telegram Download Bot

A Telegram bot that can download content from various platforms:
- Spotify (tracks, albums, playlists) in high quality with metadata
- TikTok videos without watermark
- YouTube videos in high quality
- Instagram reels and posts

## Features

- **Spotify Downloads**: Download tracks, albums, or playlists with full metadata
- **TikTok Downloads**: Download TikTok videos without watermark
- **YouTube Downloads**: Download YouTube videos in high quality
- **Instagram Downloads**: Download Instagram reels and posts

## Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/Download_Bot-TG.git
cd Download_Bot-TG
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API keys:
   - Open `bot/config.py` and add your API keys:
     - Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
     - Spotify API credentials (get from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/))
     - Other API keys as needed

4. Run the bot:
```bash
python main.py
```

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to get started
3. Send a link from any supported platform:
   - Spotify: `https://open.spotify.com/track/...`
   - TikTok: `https://www.tiktok.com/@user/video/...`
   - YouTube: `https://www.youtube.com/watch?v=...`
   - Instagram: `https://www.instagram.com/reel/...`
4. The bot will download and send you the content

## Implementation Notes

This bot uses:
- `python-telegram-bot` for the Telegram Bot API
- `spotipy` for Spotify API integration
- `youtube-dl` for YouTube video downloads
- `instaloader` for Instagram content downloads

## Disclaimer

This bot is for educational purposes only. Please respect copyright laws and terms of service of the platforms you're downloading from.

## License

MIT License
# Loadtunez - Telegram Media Downloader Bot

A Telegram bot that downloads content from Spotify, TikTok, YouTube, and Instagram.

## Features

- Download Spotify tracks, albums, and playlists
- Download TikTok videos without watermark
- Download YouTube videos in high quality
- Download Instagram reels and posts
- Search for music on Spotify

## Deployment on Render

This bot is configured to run on Render's free tier service.

### Setup Instructions

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

4. Add the following environment variables:
   - `API_TOKEN`: Your Telegram Bot API token
   - `SPOTIFY_CLIENT_ID`: Your Spotify API client ID
   - `SPOTIFY_CLIENT_SECRET`: Your Spotify API client secret
   - `PORT`: 8080 (or let Render assign one)
   - `WEBHOOK_URL`: Your Render service URL (e.g., https://loadtunez-bot.onrender.com)
   - Add any other API keys needed for TikTok, YouTube, or Instagram

### Free Tier Limitations

- Free tier instances will spin down after 15 minutes of inactivity
- They'll spin back up when a new request comes in (with a brief cold start delay)
- You get 750 free hours per month which is enough for continuous operation

## Local Development

1. Clone the repository
2. Create a `.env` file with the required environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run the bot: `python main.py`

## License

[MIT License](LICENSE)
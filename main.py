from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest, TimedOut, NetworkError
from bot.handlers.spotify import handle_spotify_url, handle_spotify_callback, search_spotify
from bot.handlers.tiktok import handle_tiktok_url
from bot.handlers.youtube import handle_youtube_url
from bot.handlers.instagram import handle_instagram_url
from bot.config import API_TOKEN, DOWNLOAD_DIRECTORY  # <-- Add DOWNLOAD_DIRECTORY to the import
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import re

# URL patterns for different platforms
SPOTIFY_PATTERN = r'(https?://(open\.spotify\.com|spotify\.link)/(track|album|playlist)/[a-zA-Z0-9]+)'
TIKTOK_PATTERN = r'(https?://(www\.)?(tiktok\.com|vm\.tiktok\.com)/[@a-zA-Z0-9_\.-]+/video/\d+)'
YOUTUBE_PATTERN = r'(https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+)'
INSTAGRAM_PATTERN = r'(https?://(www\.)?(instagram\.com/reel/[a-zA-Z0-9_-]+|instagram\.com/p/[a-zA-Z0-9_-]+))'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    # Inline keyboard for platform info
    inline_keyboard = [
        [InlineKeyboardButton("Spotify", callback_data='info_spotify')],
        [InlineKeyboardButton("TikTok", callback_data='info_tiktok')],
        [InlineKeyboardButton("YouTube", callback_data='info_youtube')],
        [InlineKeyboardButton("Instagram", callback_data='info_instagram')]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    # Persistent bottom keyboard
    bottom_keyboard = [
        [KeyboardButton("🔍 Search Spotify"), KeyboardButton("❓ Help")],
        [KeyboardButton("🎵 Spotify"), KeyboardButton("📱 TikTok")],
        [KeyboardButton("🎬 YouTube"), KeyboardButton("📸 Instagram")]
    ]
    reply_markup = ReplyKeyboardMarkup(bottom_keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        'Welcome to the Downloader Bot! 🎵📱🎬\n\n'
        'I can download content from Spotify, TikTok, YouTube, and Instagram.\n\n'
        'Simply send me a link to download content, or use the buttons below to learn more:',
        reply_markup=inline_markup
    )
    
    # Send a second message with the persistent bottom keyboard
    await update.message.reply_text(
        'I\'ve added quick access buttons at the bottom of your chat. Use them anytime!',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    
    try:
        await query.answer()
        
        data = query.data
        
        # Handle Spotify download callbacks
        if data.startswith('dl_track_') or data.startswith('dl_album_'):
            await handle_spotify_callback(update, context)
            return
        
        if data == 'info_spotify':
            await query.edit_message_text(
                "🎵 *Spotify Downloader*\n\n"
                "Send me any Spotify link to download:\n"
                "• Track: spotify.com/track/...\n"
                "• Album: spotify.com/album/...\n"
                "• Playlist: spotify.com/playlist/...\n\n"
                "Or search for music with:\n"
                "• /search [song or album name]\n\n"
                "I'll download it in high quality with all metadata!",
                parse_mode='Markdown'
            )
        elif data == 'info_tiktok':
            await query.edit_message_text(
                "📱 *TikTok Downloader*\n\n"
                "Send me any TikTok video link:\n"
                "• tiktok.com/@user/video/...\n"
                "• vm.tiktok.com/...\n\n"
                "I'll download it without watermark!",
                parse_mode='Markdown'
            )
        elif data == 'info_youtube':
            await query.edit_message_text(
                "🎬 *YouTube Downloader*\n\n"
                "Send me any YouTube link:\n"
                "• youtube.com/watch?v=...\n"
                "• youtu.be/...\n\n"
                "I'll download it in high quality!",
                parse_mode='Markdown'
            )
        elif data == 'info_instagram':
            await query.edit_message_text(
                "📸 *Instagram Downloader*\n\n"
                "Send me any Instagram link:\n"
                "• instagram.com/reel/...\n"
                "• instagram.com/p/...\n\n"
                "I'll download it in high quality!",
                parse_mode='Markdown'
            )
    except (BadRequest, TimedOut) as e:
        print(f"Callback error: {e}")
        # If the callback query is too old, we can't answer it
        # Just continue with the operation

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'How to use this bot:\n\n'
        '1. Send a link from Spotify, TikTok, YouTube, or Instagram\n'
        '2. Wait for the download to complete\n'
        '3. Receive your file!\n\n'
        'Supported platforms:\n'
        '• Spotify (tracks, albums, playlists)\n'
        '• TikTok (videos)\n'
        '• YouTube (videos)\n'
        '• Instagram (reels)\n\n'
        'Special commands:\n'
        '• /search [query] - Search for tracks and albums on Spotify\n'
        '• /help - Show this help message\n'
        '• /start - Start the bot'
    )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /search command."""
    if not context.args:
        await update.message.reply_text("Please provide a search query. Example: /search bohemian rhapsody")
        return
    
    query = ' '.join(context.args)
    await search_spotify(update, context, query)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URLs sent by the user."""
    text = update.message.text
    
    # Handle keyboard button commands
    if text == "🔍 Search Spotify":
        await update.message.reply_text("Please enter your search query after 'search'. For example: search bohemian rhapsody")
        return
    elif text == "❓ Help":
        await help_command(update, context)
        return
    elif text == "🎵 Spotify":
        await update.message.reply_text(
            "🎵 *Spotify Downloader*\n\n"
            "Send me any Spotify link to download:\n"
            "• Track: spotify.com/track/...\n"
            "• Album: spotify.com/album/...\n"
            "• Playlist: spotify.com/playlist/...\n\n"
            "Or search for music with:\n"
            "• /search [song or album name]\n\n"
            "I'll download it in high quality with all metadata!",
            parse_mode='Markdown'
        )
        return
    elif text == "📱 TikTok":
        await update.message.reply_text(
            "📱 *TikTok Downloader*\n\n"
            "Send me any TikTok video link:\n"
            "• tiktok.com/@user/video/...\n"
            "• vm.tiktok.com/...\n\n"
            "I'll download it without watermark!",
            parse_mode='Markdown'
        )
        return
    elif text == "🎬 YouTube":
        await update.message.reply_text(
            "🎬 *YouTube Downloader*\n\n"
            "Send me any YouTube link:\n"
            "• youtube.com/watch?v=...\n"
            "• youtu.be/...\n\n"
            "I'll download it in high quality!",
            parse_mode='Markdown'
        )
        return
    elif text == "📸 Instagram":
        await update.message.reply_text(
            "📸 *Instagram Downloader*\n\n"
            "Send me any Instagram link:\n"
            "• instagram.com/reel/...\n"
            "• instagram.com/p/...\n\n"
            "I'll download it in high quality!",
            parse_mode='Markdown'
        )
        return
    
    # Check for Spotify search
    if text.lower().startswith('search '):
        query = text[7:]  # Remove 'search ' prefix
        await search_spotify(update, context, query)
        return
    
    # Check for Spotify links
    if re.search(SPOTIFY_PATTERN, text):
        await handle_spotify_url(update, context)
    # Check for TikTok links
    elif re.search(TIKTOK_PATTERN, text):
        await handle_tiktok_url(update, context)
    # Check for YouTube links
    elif re.search(YOUTUBE_PATTERN, text):
        await handle_youtube_url(update, context)
    # Check for Instagram links
    elif re.search(INSTAGRAM_PATTERN, text):
        await handle_instagram_url(update, context)
    else:
        await update.message.reply_text(
            "I don't recognize this link. Please send a valid link from Spotify, TikTok, YouTube, or Instagram, "
            "or use /search [query] to search for music on Spotify."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    print(f"Update {update} caused error {context.error}")
    
    # If the error is related to a message, inform the user
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, an error occurred while processing your request. Please try again later."
        )

async def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(API_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    
    # Register callback query handler for button callbacks
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Register message handler for URLs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Create download directory if it doesn't exist
    os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)
    
    # For production deployment on Render:
    PORT = int(os.environ.get('PORT', 8080))
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
    
    # If webhook URL is provided, use webhooks, otherwise use polling
    if WEBHOOK_URL:
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{API_TOKEN}")
        await application.start()
        await application.update_webhook_info(
            url=f"{WEBHOOK_URL}/{API_TOKEN}",
            allowed_updates=["message", "callback_query"]
        )
        
        # Start the webhook server
        from telegram.ext import Updater
        updater = Updater(bot=application.bot)
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=API_TOKEN
        )
    else:
        # Fallback to polling if no webhook URL is provided
        await application.run_polling()
    
    # Run the bot until you press Ctrl-C
    await application.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
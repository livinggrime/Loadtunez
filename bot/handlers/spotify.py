import re
import os
import glob
import subprocess
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest, TimedOut
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from bot.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

def extract_spotify_id(url):
    """Extract Spotify ID and type from URL."""
    # Track pattern
    track_match = re.search(r'spotify\.com/track/([a-zA-Z0-9]+)', url)
    if track_match:
        return track_match.group(1), 'track'
    
    # Album pattern
    album_match = re.search(r'spotify\.com/album/([a-zA-Z0-9]+)', url)
    if album_match:
        return album_match.group(1), 'album'
    
    # Playlist pattern
    playlist_match = re.search(r'spotify\.com/playlist/([a-zA-Z0-9]+)', url)
    if playlist_match:
        return playlist_match.group(1), 'playlist'
    
    return None, None

async def handle_spotify_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Spotify URLs."""
    url = update.message.text
    spotify_id, content_type = extract_spotify_id(url)
    
    if not spotify_id:
        # Check if it's a search query
        if url.lower().startswith('/search ') or url.lower().startswith('search '):
            query = url.split(' ', 1)[1]
            await search_spotify(update, context, query)
            return
        await update.message.reply_text("Invalid Spotify URL. Please provide a valid Spotify track, album, or playlist link.")
        return
    
    if content_type == 'track':
        await download_single_track(update.message, spotify_id)
    elif content_type == 'album':
        await update.message.reply_text("Album downloads are not supported. Please send individual track links.")
    elif content_type == 'playlist':
        await update.message.reply_text("Playlist downloads are not supported. Please send individual track links.")

async def search_spotify(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str) -> None:
    """Search for tracks and albums on Spotify."""
    await update.message.reply_text(f"🔍 Searching Spotify for: *{query}*", parse_mode='Markdown')
    
    try:
        # Search for tracks
        track_results = sp.search(q=query, type='track', limit=5)
        tracks = track_results['tracks']['items']
        
        if not tracks:
            await update.message.reply_text(f"❌ No results found for: *{query}*", parse_mode='Markdown')
            return
        
        # Create keyboard for tracks
        keyboard = []
        
        if tracks:
            await update.message.reply_text("🎵 *Tracks:*", parse_mode='Markdown')
            for i, track in enumerate(tracks):
                track_name = track['name']
                artists = ', '.join([artist['name'] for artist in track['artists']])
                track_id = track['id']
                
                # Create button for each track
                keyboard.append([InlineKeyboardButton(
                    f"{i+1}. {track_name} - {artists}",
                    callback_data=f"dl_track_{track_id}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Select a track to download:", reply_markup=reply_markup)
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error searching Spotify: {str(e)}")

async def handle_spotify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Spotify callback queries."""
    query = update.callback_query
    
    try:
        # Try to answer the callback query, but don't fail if it's too old
        try:
            await query.answer()
        except (BadRequest, TimedOut):
            pass
        
        data = query.data
        
        if data.startswith('dl_track_'):
            track_id = data.replace('dl_track_', '')
            try:
                await query.edit_message_text(f"Starting track download...")
            except (BadRequest, TimedOut):
                # If we can't edit the message, send a new one
                await query.message.reply_text(f"Starting track download...")
            
            # Get track info
            track = sp.track(track_id)
            track_name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            
            # Send a direct message instead of trying to edit the callback message
            await query.message.reply_text(f"🎵 Downloading: *{track_name}* by *{artists}*", parse_mode='Markdown')
            await download_single_track(query.message, track_id)
    except Exception as e:
        # If any error occurs, send a new message
        await query.message.reply_text(f"❌ Error processing request: {str(e)}")

async def download_single_track(update, track_id):
    """Download a single Spotify track using spotdl and send to user with metadata and cover."""
    try:
        # Get track info
        track = sp.track(track_id)
        track_name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        cover_url = track['album']['images'][0]['url'] if track['album']['images'] else None

        # Generate a YouTube search link as fallback
        search_query = f"{artists} - {track_name} audio"
        youtube_search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
        keyboard = [[InlineKeyboardButton("Search on YouTube", url=youtube_search_url)]]
        fallback_markup = InlineKeyboardMarkup(keyboard)

        # Notify user
        status_message = await update.reply_text(f"🎵 Downloading: *{track_name}* by *{artists}*", parse_mode='Markdown')

        # Download with spotdl
        DOWNLOAD_DIRECTORY = os.environ.get("DOWNLOAD_DIRECTORY", "/tmp")
        url = f"https://open.spotify.com/track/{track_id}"
        
        # Check if ffmpeg is installed
        try:
            ffmpeg_check = subprocess.run(['ffmpeg', '-version'], shell=True, capture_output=True, text=True)
            if ffmpeg_check.returncode != 0:
                await update.reply_text("❌ FFmpeg is not installed. Please install FFmpeg to download tracks.")
                return
        except Exception:
            await update.reply_text("❌ FFmpeg is not installed. Please install FFmpeg to download tracks.")
            return
            
        cmd = f'spotdl --output "{DOWNLOAD_DIRECTORY}" "{url}"'
        print("Running command:", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print("spotdl stdout:", result.stdout)
        print("spotdl stderr:", result.stderr)

        # Find the newest mp3 file
        mp3_files = glob.glob(os.path.join(DOWNLOAD_DIRECTORY, "*.mp3"))
        if not mp3_files:
            print("No mp3 files found in", DOWNLOAD_DIRECTORY)
            await update.reply_text(
                f"❌ Error downloading track. You can try finding it on YouTube:",
                reply_markup=fallback_markup
            )
            return

        latest_file = max(mp3_files, key=os.path.getctime)
        file_size = os.path.getsize(latest_file)
        print("Downloaded file:", latest_file, "Size:", file_size)

        if file_size == 0:
            await update.reply_text(
                f"❌ Downloaded file is empty. You can try finding it on YouTube:",
                reply_markup=fallback_markup
            )
            os.remove(latest_file)
            return

        if file_size > 50 * 1024 * 1024:
            await update.reply_text("❌ The downloaded file is too large for Telegram (max 50MB).")
            os.remove(latest_file)
            return

        # Download cover art if available
        thumb_path = None
        if cover_url:
            try:
                thumb_path = os.path.join(DOWNLOAD_DIRECTORY, "cover.jpg")
                with open(thumb_path, "wb") as img_file:
                    img_file.write(requests.get(cover_url).content)
            except Exception as e:
                print("Error downloading cover art:", e)
                thumb_path = None

        # Send audio with metadata and cover
        try:
            with open(latest_file, 'rb') as audio_file:
                await update.reply_audio(
                    audio=audio_file,
                    title=track_name,
                    performer=artists,
                    caption=f"Album: {album_name}",
                    thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None
                )
        except Exception as send_error:
            print("Error sending audio:", send_error)
            await update.reply_text("❌ Error sending audio file.")

        # Clean up
        os.remove(latest_file)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)

        await status_message.edit_text(f"✅ Sent: *{track_name}* by *{artists}*", parse_mode='Markdown')

    except Exception as e:
        print("General error:", e)
        await update.reply_text(f"❌ Error processing track: {str(e)}")
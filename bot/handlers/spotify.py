import re
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bot.utils.downloader import download_spotify_track, ensure_directory_exists
from bot.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, DOWNLOAD_DIRECTORY

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

def handle_spotify_url(update: Update, context: CallbackContext) -> None:
    """Handle Spotify URLs."""
    url = update.message.text
    spotify_id, content_type = extract_spotify_id(url)
    
    if not spotify_id:
        # Check if it's a search query
        if url.lower().startswith('/search ') or url.lower().startswith('search '):
            query = url.split(' ', 1)[1]
            search_spotify(update, context, query)
            return
        update.message.reply_text("Invalid Spotify URL. Please provide a valid Spotify track, album, or playlist link.")
        return
    
    if content_type == 'track':
        download_single_track(update, spotify_id)
    elif content_type == 'album':
        update.message.reply_text("Album downloads are not supported. Please send individual track links.")
    elif content_type == 'playlist':
        update.message.reply_text("Playlist downloads are not supported. Please send individual track links.")

def search_spotify(update: Update, context: CallbackContext, query: str) -> None:
    """Search for tracks and albums on Spotify."""
    update.message.reply_text(f"🔍 Searching Spotify for: *{query}*", parse_mode='Markdown')
    
    try:
        # Search for tracks
        track_results = sp.search(q=query, type='track', limit=5)
        tracks = track_results['tracks']['items']
        
        if not tracks:
            update.message.reply_text(f"❌ No results found for: *{query}*", parse_mode='Markdown')
            return
        
        # Create keyboard for tracks
        keyboard = []
        
        if tracks:
            update.message.reply_text("🎵 *Tracks:*", parse_mode='Markdown')
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
            update.message.reply_text("Select a track to download:", reply_markup=reply_markup)
            
    except Exception as e:
        update.message.reply_text(f"❌ Error searching Spotify: {str(e)}")

def handle_spotify_callback(update: Update, context: CallbackContext) -> None:
    """Handle Spotify callback queries."""
    query = update.callback_query
    query.answer()
    
    data = query.data
    
    if data.startswith('dl_track_'):
        track_id = data.replace('dl_track_', '')
        query.edit_message_text(f"Starting track download...")
        download_single_track(query, track_id)

def download_single_track(update, track_id):
    """Download a single Spotify track directly to memory and send to user."""
    try:
        # Get track info
        track = sp.track(track_id)
        track_name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        
        update.message.reply_text(f"🎵 Downloading track: *{track_name}* by *{artists}*", parse_mode='Markdown')
        
        # Download the track to a temporary file
        result = download_spotify_track(track_id)
        
        if not result.get("success", False):
            update.message.reply_text(f"❌ Error downloading track: {result.get('error', 'Unknown error')}")
            return
            
        # Get the file path
        temp_path = result.get("path")
        
        if not os.path.exists(temp_path):
            update.message.reply_text(f"❌ Downloaded file not found")
            return
            
        # Check file size
        file_size = os.path.getsize(temp_path)
        if file_size == 0:
            update.message.reply_text("❌ Downloaded file is empty")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return
            
        # Send the downloaded file
        update.message.reply_text(f"✅ Downloaded: *{track_name}* by *{artists}*\nSending file...", parse_mode='Markdown')
        
        try:
            with open(temp_path, 'rb') as audio_file:
                update.message.reply_audio(
                    audio=audio_file,
                    title=track_name,
                    performer=artists,
                    caption=f"Album: {album_name}"
                )
        except Exception as send_error:
            update.message.reply_text(f"❌ Error sending audio file: {str(send_error)}")
            # Try sending as document if audio fails
            try:
                with open(temp_path, 'rb') as doc_file:
                    update.message.reply_document(
                        document=doc_file,
                        caption=f"{track_name} by {artists} (Album: {album_name})"
                    )
            except Exception as doc_error:
                update.message.reply_text(f"❌ Error sending document: {str(doc_error)}")
        
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        update.message.reply_text(f"❌ Error downloading track: {str(e)}")
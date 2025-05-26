import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bot.utils.downloader import download_spotify_track, ensure_directory_exists
from bot.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, DOWNLOAD_DIRECTORY
import os

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
    
    # Ensure download directory exists
    ensure_directory_exists(DOWNLOAD_DIRECTORY)
    
    if content_type == 'track':
        download_single_track(update, spotify_id)
    elif content_type == 'album':
        download_album(update, spotify_id)
    elif content_type == 'playlist':
        download_playlist(update, spotify_id)

def search_spotify(update: Update, context: CallbackContext, query: str) -> None:
    """Search for tracks and albums on Spotify."""
    update.message.reply_text(f"🔍 Searching Spotify for: *{query}*", parse_mode='Markdown')
    
    try:
        # Search for tracks
        track_results = sp.search(q=query, type='track', limit=5)
        tracks = track_results['tracks']['items']
        
        # Search for albums
        album_results = sp.search(q=query, type='album', limit=5)
        albums = album_results['albums']['items']
        
        if not tracks and not albums:
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
        
        # Create keyboard for albums
        keyboard = []
        
        if albums:
            update.message.reply_text("💿 *Albums:*", parse_mode='Markdown')
            for i, album in enumerate(albums):
                album_name = album['name']
                artist_name = album['artists'][0]['name']
                album_id = album['id']
                
                # Create button for each album
                keyboard.append([InlineKeyboardButton(
                    f"{i+1}. {album_name} - {artist_name}",
                    callback_data=f"dl_album_{album_id}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Select an album to download:", reply_markup=reply_markup)
            
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
    elif data.startswith('dl_album_'):
        album_id = data.replace('dl_album_', '')
        query.edit_message_text(f"Starting album download...")
        download_album(query, album_id)

def download_single_track(update, track_id):
    """Download a single Spotify track."""
    try:
        # Get track info
        track = sp.track(track_id)
        track_name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        
        update.message.reply_text(f"🎵 Downloading track: *{track_name}* by *{artists}*", parse_mode='Markdown')
        
        # Download the track
        output_path = os.path.join(DOWNLOAD_DIRECTORY, f"{artists} - {track_name}.mp3")
        result = download_spotify_track(track_id, output_path)
        
        if not result.get("success", False):
            update.message.reply_text(f"❌ Error downloading track: {result.get('error', 'Unknown error')}")
            return
            
        # Get the actual file path (might be different from requested path)
        actual_path = result.get("path", output_path)
        
        if not os.path.exists(actual_path):
            update.message.reply_text(f"❌ Downloaded file not found at {actual_path}")
            return
            
        # Check file size
        file_size = os.path.getsize(actual_path)
        if file_size == 0:
            update.message.reply_text("❌ Downloaded file is empty")
            return
            
        # Send the downloaded file
        update.message.reply_text(f"✅ Downloaded: *{track_name}* by *{artists}*\nFile size: {file_size/1024/1024:.2f} MB", parse_mode='Markdown')
        
        try:
            with open(actual_path, 'rb') as audio_file:
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
                with open(actual_path, 'rb') as doc_file:
                    update.message.reply_document(
                        document=doc_file,
                        caption=f"{track_name} by {artists} (Album: {album_name})"
                    )
            except Exception as doc_error:
                update.message.reply_text(f"❌ Error sending document: {str(doc_error)}")
    except Exception as e:
        update.message.reply_text(f"❌ Error downloading track: {str(e)}")

def download_album(update, album_id):
    """Download all tracks from a Spotify album."""
    try:
        # Get album info
        album = sp.album(album_id)
        album_name = album['name']
        artist_name = album['artists'][0]['name']
        
        update.message.reply_text(f"💿 Downloading album: *{album_name}* by *{artist_name}*\nThis may take a while...", parse_mode='Markdown')
        
        # Get all tracks from the album
        results = sp.album_tracks(album_id)
        tracks = results['items']
        
        # Create album directory
        album_dir = os.path.join(DOWNLOAD_DIRECTORY, f"{artist_name} - {album_name}")
        ensure_directory_exists(album_dir)
        
        # Download each track
        for i, track in enumerate(tracks):
            track_name = track['name']
            track_number = track['track_number']
            track_id = track['id']
            
            update.message.reply_text(f"Downloading track {i+1}/{len(tracks)}: {track_name}")
            
            output_path = os.path.join(album_dir, f"{track_number:02d} - {track_name}.mp3")
            download_spotify_track(track_id, output_path)
        
        update.message.reply_text(f"✅ Album *{album_name}* downloaded successfully!", parse_mode='Markdown')
    except Exception as e:
        update.message.reply_text(f"❌ Error downloading album: {str(e)}")

def download_playlist(update, playlist_id):
    """Download all tracks from a Spotify playlist."""
    try:
        # Get playlist info
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist['name']
        
        update.message.reply_text(f"📋 Downloading playlist: *{playlist_name}*\nThis may take a while...", parse_mode='Markdown')
        
        # Get all tracks from the playlist
        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']
        
        # Create playlist directory
        playlist_dir = os.path.join(DOWNLOAD_DIRECTORY, f"Playlist - {playlist_name}")
        ensure_directory_exists(playlist_dir)
        
        # Download each track
        for i, item in enumerate(tracks):
            track = item['track']
            track_name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            track_id = track['id']
            
            update.message.reply_text(f"Downloading track {i+1}/{len(tracks)}: {track_name} by {artists}")
            
            output_path = os.path.join(playlist_dir, f"{i+1:02d} - {artists} - {track_name}.mp3")
            download_spotify_track(track_id, output_path)
        
        update.message.reply_text(f"✅ Playlist *{playlist_name}* downloaded successfully!", parse_mode='Markdown')
    except Exception as e:
        update.message.reply_text(f"❌ Error downloading playlist: {str(e)}")
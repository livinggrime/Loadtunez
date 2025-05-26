def format_track_data(track):
    return {
        "title": track.get("title"),
        "artist": track.get("artist"),
        "album": track.get("album"),
        "duration": track.get("duration"),
        "url": track.get("url"),
    }

def format_video_data(video):
    return {
        "title": video.get("title"),
        "uploader": video.get("uploader"),
        "duration": video.get("duration"),
        "url": video.get("url"),
    }

def manage_api_request(url, params=None):
    import requests
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
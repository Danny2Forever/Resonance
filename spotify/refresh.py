import spotipy
from django.utils import timezone
from .models import UserMusicProfile
from collections import Counter

from spotipy.oauth2 import SpotifyOAuth
from django.utils import timezone
from django.conf import settings

def ensure_valid_spotify_token(user):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPES,
        show_dialog=True
    )

    token_info = {
        "access_token": user.access_token,
        "refresh_token": user.refresh_token,
        "expires_at": user.token_expires_at.timestamp() 
    }

    if sp_oauth.is_token_expired(token_info):
        token = sp_oauth.refresh_access_token(user.refresh_token)
        user.access_token = token_info["access_token"]
        user.token_expires_at = timezone.now() + timezone.timedelta(seconds=token["expires_in"])
        user.save()

    return user.access_token

def refresh_user_profile(user):
    access_token = ensure_valid_spotify_token(user)
    sp = spotipy.Spotify(auth=access_token)

    top_artists_data = sp.current_user_top_artists(limit=10, time_range="medium_term")
    top_tracks_data = sp.current_user_top_tracks(limit=10, time_range="medium_term")
    top_artists = [{"id": a["id"], "name": a["name"], "genres": a["genres"], "images": a["images"][-1]} for a in top_artists_data["items"]]
    top_tracks = [{"id": t["id"], "name": t["name"], "artists": [a["name"] for a in t["artists"]], "images": t["album"]["images"][-1]} for t in top_tracks_data["items"]]
    genres = [g for artist in top_artists for g in artist["genres"][:3]]  # เอาแค่ 3 genres แรกของแต่ละ artist

    genres_count = Counter(genres)
    genres_freq = genres_count.most_common(5)

    total_top5 = sum(count for _, count in genres_freq) or 1
    genres_percentage = [
        (genre, round((count / total_top5) * 100, 2)) for genre, count in genres_freq
    ]

    profile, _ = UserMusicProfile.objects.update_or_create(
        user=user,
        defaults={
            "top_artists": top_artists,
            "top_tracks": top_tracks,
            "genres": genres_percentage,
            "last_refreshed": timezone.now(),
        },
    )

    return profile, print(f"Refreshed profile for user {user.spotify_id}")

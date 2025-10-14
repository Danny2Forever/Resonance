from .models import UserMusicProfile
from collections import Counter

from spotipy.oauth2 import SpotifyOAuth
from django.utils import timezone
from django.conf import settings
from users.service import get_current_user

from users.spotify_utils import get_spotify_client

def refresh_user_profile(request):
    sp = get_spotify_client(request)
    if not sp:
        return None

    user = get_current_user(request)
    if not user:
        return None
    
    top_artists_data = sp.current_user_top_artists(limit=10, time_range="medium_term")
    top_tracks_data = sp.current_user_top_tracks(limit=10, time_range="medium_term")
    top_artists = [{"id": a["id"], "name": a["name"], "genres": a["genres"], "images": a["images"][-1]} for a in top_artists_data["items"]]
    top_tracks = [{"id": t["id"], "name": t["name"], "artists": [a["name"] for a in t["artists"]], "images": t["album"]["images"][-1]} for t in top_tracks_data["items"]]
    genres = []
    for artist in top_artists:
        top3_genres = artist["genres"][:3]
        for g in top3_genres:
            genres.append(g)  # เอาแค่ 3 genres แรกของแต่ละ artist

    genres_count = Counter(genres)
    genres_freq = genres_count.most_common(5)

    total_top5 = 0
    for genre, count in genres_freq:
        total_top5 += count

    if total_top5 == 0:
        total_top5 = 1

    genres_percentage = []
    for genre, count in genres_freq:
        percent = (count / total_top5) * 100
        genres_percentage.append((genre, round(percent, 2)))

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

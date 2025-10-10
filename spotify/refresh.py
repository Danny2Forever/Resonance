import spotipy
from django.utils import timezone
from .models import UserMusicProfile

def refresh_user_profile(user):
    sp = spotipy.Spotify(auth=user.access_token)

    top_artists_data = sp.current_user_top_artists(limit=10, time_range="medium_term")
    top_tracks_data = sp.current_user_top_tracks(limit=10, time_range="medium_term")
    top_artists = [{"id": a["id"], "name": a["name"], "genres": a["genres"], "images": a["images"][-1]} for a in top_artists_data["items"]]
    top_tracks = [{"id": t["id"], "name": t["name"], "artists": [a["name"] for a in t["artists"]]} for t in top_tracks_data["items"]]
    genres = list({g for artist in top_artists for g in artist["genres"][:3]})

    profile, _ = UserMusicProfile.objects.update_or_create(
        user=user,
        defaults={
            "top_artists": top_artists,
            "top_tracks": top_tracks,
            "genres": genres,
            "last_refreshed": timezone.now(),
        },
    )

    return profile, print(f"Refreshed profile for user {user.spotify_id}")

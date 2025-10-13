'''function for use'''
import spotipy
from .models import MutualPlaylist

def jaccard_similarity(genres1, genres2):
    """ genres1, genres2: list of tuples [(genre_name, count), ...] """
    set1 = set([g[0] for g in genres1])
    set2 = set([g[0] for g in genres2])

    if not set1 and not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union

def create_mutual_playlist(user1, user2, playlist_name="Mutual Playlist"):
    """Create a mutual playlist for two users."""
    sp = spotipy.Spotify(auth=user1.access_token)

    # รวม top tracks ของทั้งสอง
    user1_tracks = [top["id"] for top in user1.music_profile.top_tracks]
    user2_tracks = [top["id"] for top in user2.music_profile.top_tracks]

    track_ids = list(set(user1_tracks + user2_tracks))  # unique tracks

    # สร้าง playlist บน user1
    playlist = sp.user_playlist_create(
        user=user1.spotify_id,
        name=playlist_name,
        public=False,
        description=f"Mutual playlist of {user1.username} & {user2.username}"
    )

    sp.playlist_add_items(playlist_id=playlist["id"], items=track_ids[:50])  # Spotify limit: 100
    
    mutual_playlist = MutualPlaylist.objects.create(
        user=user1,
        name=playlist["name"],
        description=playlist.get("description", ""),
        playlist_url=playlist["external_urls"]["spotify"]
    ) # สร้าง mutual_playlist

    return mutual_playlist

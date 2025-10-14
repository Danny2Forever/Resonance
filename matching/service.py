from users.spotify_utils import get_spotify_client
from .models import MutualPlaylist, User

def flatten_list(data):
    '''แปลงรายการที่อาจมีการซ้อนกัน [[1], 2, [3, 4]] เป็น [1, 2, 3, 4]'''
    if not data or not isinstance(data, list):
        return []
    flat_list = []
    for item in data:
        if isinstance(item, list):
            for sub_item in item:
                flat_list.append(str(sub_item))
        else:
            flat_list.append(str(item))
    return flat_list


def jaccard_similarity(list1, list2):
    """Calculates the Jaccard similarity between two lists, handling potential nesting."""
    set1 = set(flatten_list(list1))
    # print(set1)
    set2 = set(flatten_list(list2))
    # print(set2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union else 0.0


def create_mutual_playlist(request, user1: User, user2: User):
    """
    Creates a mutual playlist on Spotify using a valid token, saves a record
    locally, and returns the MutualPlaylist database object.
    """
    sp = get_spotify_client(request)
    if not sp:
        return None

    # Safely get the profile objects for each user
    user1_profile = getattr(user1, 'music_profile', None)
    user2_profile = getattr(user2, 'music_profile', None)

    # Safely get the top tracks by accessing the attribute directly
    user1_top_tracks = getattr(user1_profile, 'top_tracks', []) if user1_profile else []
    user2_top_tracks = getattr(user2_profile, 'top_tracks', []) if user2_profile else []

    user1_top_track_ids = {track['id'] for track in user1_top_tracks}
    user2_top_track_ids = {track['id'] for track in user2_top_tracks}
    
    mutual_track_ids = list(user1_top_track_ids.intersection(user2_top_track_ids))

    if not mutual_track_ids:
        return None

    playlist_name = f"♫ {user1.username} & {user2.username}'s Mix"
    playlist_description = f"Songs you both love. Matched on Resonance."
    
    try:
        spotify_playlist = sp.user_playlist_create(
            user=user1.spotify_id, name=playlist_name, public=False, description=playlist_description
        )
        sp.playlist_add_items(spotify_playlist["id"], mutual_track_ids[:100])
        new_playlist_obj = MutualPlaylist.objects.create(
            user=user1,
            name=playlist_name,
            description=playlist_description,
            spotify_playlist_id=spotify_playlist["id"],
            spotify_url=spotify_playlist["external_urls"]["spotify"]
        )
        return new_playlist_obj
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None

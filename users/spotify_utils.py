import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
import time
from .models import User

def get_spotify_client(request):
    """
    Handles Spotify authentication for a logged-in user.

    It checks if the user's access token is expired, refreshes it if necessary,
    and returns a valid Spotipy client.
    """
    try:
        # store spotify_id in the session after login
        spotify_id = request.session.get("spotify_id")
        if not spotify_id:
            return None
        
        user = User.objects.get(spotify_id=spotify_id)

        # Construct token_info dictionary
        token_info = {
            'access_token': user.access_token,
            'refresh_token': user.refresh_token,
            'expires_at': getattr(user, 'token_expires_at', 0) 
        }

        # Check if the token is expired or will expire in the next 60 seconds
        now = int(time.time())
        is_expired = token_info['expires_at'] - now < 60

        if is_expired:
            sp_oauth = SpotifyOAuth(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIFY_REDIRECT_URI,
                scope="user-read-email user-read-private user-top-read playlist-modify-private playlist-modify-public"
            )
            
            # Refresh the token
            new_token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

            # Update the user's tokens and expiration time in your database
            user.access_token = new_token_info['access_token']
            user.refresh_token = new_token_info.get('refresh_token', user.refresh_token)
            # user.token_expires_at = new_token_info['expires_at'] 
            user.save()
            
            # Use the new token for the client
            return spotipy.Spotify(auth=new_token_info['access_token'])

        # If token is not expired, use the existing one
        return spotipy.Spotify(auth=user.access_token)

    except User.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error getting spotify client: {e}") # for debugging
        return None
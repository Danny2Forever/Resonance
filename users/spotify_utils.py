import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
import time
from .models import User
from django.shortcuts import redirect
from datetime import datetime, timezone


def get_spotify_client(request):
    """
    เรียกใช้ฟังก์ชันนี้เพื่อใช้ Spotipy client
    """
    try:
        spotify_id = request.session.get("spotify_id")
        if not spotify_id:
            return redirect('spotify_login')
        
        user = User.objects.get(spotify_id=spotify_id)

        expires_at = user.token_expires_at
        token_info = {
            'access_token': user.access_token,
            'refresh_token': user.refresh_token,
            'expires_at': expires_at,
        }

        # check token expired
        now = datetime.now(tz=timezone.utc)
        time_range = ((now-expires_at).total_seconds()/60)
        # print(type(expires_at), expires_at)  # Debugging line
        is_expired = time_range >= 60 # หมดอายุเกิน 60 นาที

        if is_expired:
            sp_oauth = SpotifyOAuth(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIFY_REDIRECT_URI,
                scope="user-read-email user-read-private user-top-read playlist-modify-private playlist-modify-public"
            )
            

            new_token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

            # อัปเดตข้อมูล token ในฐานข้อมูล
            user.access_token = new_token_info['access_token']
            user.refresh_token = new_token_info.get('refresh_token', user.refresh_token)
            print(type(new_token_info['expires_at'])) # timestamp
            user.token_expires_at = datetime.fromtimestamp(new_token_info['expires_at'], tz=timezone.utc)
            user.save()
            
            # refresh token
            return spotipy.Spotify(auth=new_token_info['access_token'])
        # If token is not expired use current token
        return spotipy.Spotify(auth=user.access_token)

    except User.DoesNotExist:
        return redirect('spotify_login')
    except Exception as e:
        print(f"Error getting spotify client: {e}") # for debugging
        return None

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.views import View
from .models import User
from spotify.models import UserMusicProfile
from spotipy.oauth2 import SpotifyOAuth
from .forms import UserForm
from spotify.refresh import refresh_user_profile
from users.service import get_current_user
import spotipy
from django.utils import timezone

# Login
class SpotifyLoginView(View): # ถ้าผู้ใช้ได้ login แล้ว (sessionของ spotify id ยังอยู่) เมื่อเรียกหา path login จะถูกไล่ไป profile_detail
    def get(self, request):
        spotify_id = request.session.get("spotify_id") # เช็ค session
        current_user = User.objects.filter(spotify_id=spotify_id).first() # หากม่ใช้ filter มีโอกาส session ขาดหาย
        if current_user:
            user = get_object_or_404(User, spotify_id=current_user.spotify_id)
            return render(request, "profile_detail.html", {
                "user": user,
                "current_user": current_user,
            })
    
        # ถ้า user ยังไม่ login สร้าง auth URL ผ่าน SpotifyOAuth
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope=settings.SPOTIFY_SCOPES,
            show_dialog=True
        )
        auth_url = sp_oauth.get_authorize_url()

        return redirect(auth_url)

# Callback
class SpotifyCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return redirect('spotify_login')
        token_url = "https://accounts.spotify.com/api/token"
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
            'client_id': settings.SPOTIFY_CLIENT_ID,
            'client_secret': settings.SPOTIFY_CLIENT_SECRET,
        }
        resp = requests.post(token_url, data=payload)
        if resp.status_code != 200:
            return HttpResponse(f"Token error: {resp.status_code} - {resp.text}")

        tokens = resp.json()
        if 'error' in tokens:
            return HttpResponse(f"Spotify token error: {tokens['error_description']}")

        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        token_expires_at = timezone.now() + timezone.timedelta(seconds=tokens["expires_in"])
        # แบบไม่ใช้ spotipy
        # headers = {"Authorization": f"Bearer {access_token}"}
        # profile_resp = requests.get("https://api.spotify.com/v1/me", headers=headers)
        # if profile_resp.status_code != 200:
        #     return HttpResponse(f"Spotify API error: {profile_resp.status_code} - {profile_resp.text}")

        # ใช้ Spotipy ดึงข้อมูลแทน requests.get
        sp = spotipy.Spotify(auth=access_token)
        profile = sp.current_user()

        spotify_id = profile.get('id')
        username = profile.get('display_name', spotify_id)
        email = profile.get('email', '')

        try:
            user = User.objects.get(spotify_id=spotify_id)
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.token_expires_at = token_expires_at
            user.save()
            refresh_user_profile(request)
            request.session['spotify_id'] = user.spotify_id # เก็บ spotify_id ลง session
            return redirect('profile_detail', spotify_id=user.spotify_id)
        except User.DoesNotExist:
            user = User.objects.create(
                spotify_id=spotify_id,
                username=username,
                email=email,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at
            )
        
        refresh_user_profile(request)
        request.session['spotify_id'] = user.spotify_id
        return redirect('edit_profile', spotify_id=user.spotify_id)

# Edit profile
class EditProfileView(View):
    def get(self, request, spotify_id):
        user = get_object_or_404(User, spotify_id=spotify_id)
        current_user = get_current_user(request)
        if not current_user.is_admin:
            if not current_user or current_user.spotify_id != user.spotify_id:
                return HttpResponse("Not authorized to edit this profile.", status=403)
        
        form = UserForm(instance=user)
        return render(request, 'profile/edit_profile.html', {'form': form, 'current_user': current_user})

    def post(self, request, spotify_id):
        user = get_object_or_404(User, spotify_id=spotify_id)
        current_user = get_current_user(request)
        if not current_user.is_admin:
            if not current_user or current_user.spotify_id != user.spotify_id:
                return HttpResponse("Not authorized to edit this profile.", status=403)

        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            refresh_user_profile(request)
            return redirect('profile_detail', spotify_id=user.spotify_id)

        return render(request, 'profile/edit_profile.html', {'form': form, 'current_user': current_user})

# Show profile
class ProfileDetailView(View):
    def get(self, request, spotify_id):
        current_user = get_current_user(request)
        user = get_object_or_404(User, spotify_id=spotify_id)
        user_music_profile = get_object_or_404(UserMusicProfile, user__spotify_id=spotify_id)
        if not current_user:
            return HttpResponse("Not logged in.", status=403)
        
        if user.favorite_song:
            user.favorite_song = user.favorite_song.replace("open.spotify.com/track", "open.spotify.com/embed/track")

        return render(request, 'profile/profile_detail.html', {
            'user': user,
            'current_user': current_user,
            'user_music_profile': user_music_profile,
        })


# Logout
class SpotifyLogoutView(View):
    def get(self, request):
        request.session.flush()
        return redirect('landing')

class LandingPageView(View):
    def get(self, request):
        spotify_id = request.session.get("spotify_id")
        if spotify_id:
            return redirect('profile_detail', spotify_id=spotify_id)
        return render(request, "landing.html")

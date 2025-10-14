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
import spotipy
from django.utils import timezone
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class SpotifyLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('profile_detail', spotify_id=request.user.spotify_id)
    
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope=settings.SPOTIFY_SCOPES,
            show_dialog=True
        )
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

class SpotifyCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return redirect('spotify_login')
        
        token_url = "https://accounts.spotify.com/api/token"
        payload = {
            'grant_type': 'authorization_code', 'code': code,
            'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
            'client_id': settings.SPOTIFY_CLIENT_ID, 'client_secret': settings.SPOTIFY_CLIENT_SECRET,
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
        
        sp = spotipy.Spotify(auth=access_token)
        profile = sp.current_user()
        spotify_id = profile.get('id')

        user, created = User.objects.update_or_create(
            spotify_id=spotify_id,
            defaults={
                'username': profile.get('display_name', spotify_id),
                'email': profile.get('email', ''),
                'access_token': access_token, 'refresh_token': refresh_token,
                'token_expires_at': token_expires_at,
            }
        )
        
        refresh_user_profile(user)
        login(request, user, backend='users.backends.SpotifyBackend')
        
        if created:
            return redirect('edit_profile', spotify_id=user.spotify_id)
        else:
            return redirect('profile_detail', spotify_id=user.spotify_id)

class EditProfileView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        user_to_edit = get_object_or_404(User, spotify_id=self.kwargs['spotify_id'])
        return (self.request.user.spotify_id == user_to_edit.spotify_id) or self.request.user.is_admin

    def get(self, request, spotify_id):
        user = get_object_or_404(User, spotify_id=spotify_id)
        form = UserForm(instance=user)
        return render(request, 'profile/edit_profile.html', {'form': form})

    def post(self, request, spotify_id):
        user = get_object_or_404(User, spotify_id=spotify_id)
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            refresh_user_profile(request)
            return redirect('profile_detail', spotify_id=user.spotify_id)
        return render(request, 'profile/edit_profile.html', {'form': form})

class ProfileDetailView(LoginRequiredMixin, View):
    def get(self, request, spotify_id):
        user_to_view = get_object_or_404(User, spotify_id=spotify_id)
        user_music_profile = get_object_or_404(UserMusicProfile, user__spotify_id=spotify_id)

        if user_to_view.favorite_song:
            user_to_view.favorite_song = user_to_view.favorite_song.replace("open.spotify.com/track", "open.spotify.com/embed/track")

        return render(request, 'profile/profile_detail.html', {
            'user': user_to_view,
            'user_music_profile': user_music_profile,
        })

class SpotifyLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('landing')

class LandingPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('profile_detail', spotify_id=request.user.spotify_id)
        return render(request, "landing.html")
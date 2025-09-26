import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.views import View
from .models import User
from .forms import UserForm

# Login
class spotify_login(View): # ถ้าผู้ใช้ได้ login แล้ว (sessionของ spotify id ยังอยู่) เมื่อเรียกหา path login จะถูกไล่ไป profile_detail
    def get(self, request):
        current_id = request.session.get("spotify_id")
        current_user = User.objects.filter(spotify_id=current_id).first()
        if not current_user:
            auth_url = (
                "https://accounts.spotify.com/authorize"
                f"?response_type=code"
                f"&client_id={settings.SPOTIFY_CLIENT_ID}"
                f"&scope={settings.SPOTIFY_SCOPES}"
                f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
                f"&show_dialog=true"
            )
            return render(request, "login.html", {"spotify_auth_url": auth_url})
        else:
            user = get_object_or_404(User, spotify_id=current_user.spotify_id)
            return render(request, 'profile_detail.html', {
                'user': user,
                'current_user': current_user,

            })

# Callback
class spotify_callback(View):
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

        headers = {"Authorization": f"Bearer {access_token}"}
        profile_resp = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if profile_resp.status_code != 200:
            return HttpResponse(f"Spotify API error: {profile_resp.status_code} - {profile_resp.text}")

        profile = profile_resp.json()
        spotify_id = profile.get('id')
        username = profile.get('display_name', spotify_id)
        email = profile.get('email', '')

        try:
            user = User.objects.get(spotify_id=spotify_id)
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.save()
            request.session['spotify_id'] = user.spotify_id # เก็บ spotify_id ลง session
            return redirect('profile_detail', spotify_id=user.spotify_id)
        except User.DoesNotExist:
            user = User.objects.create(
                spotify_id=spotify_id,
                username=username,
                email=email,
                access_token=access_token,
                refresh_token=refresh_token
            )
        request.session['spotify_id'] = user.spotify_id
        return redirect('edit_profile', spotify_id=user.spotify_id)

# Edit profile
class edit_profile(View):
    def valid_user(self, request, spotify_id):
        user = get_object_or_404(User, spotify_id=spotify_id)

        current_id = request.session.get("spotify_id")
        current_user = User.objects.filter(spotify_id=current_id).first()

        if not current_user:
            return None, None, HttpResponse("Not logged in.", status=403)
        if current_user.spotify_id != user.spotify_id and not current_user.is_admin:
            return None, None, HttpResponse("You don't have permission to edit this profile.", status=403)

        return user, current_user, None

    def get(self, request, spotify_id):
        user, current_user, error = self.valid_user(request, spotify_id)
        if error:
            return error

        form = UserForm(instance=user)
        return render(request, 'edit_profile.html', {'form': form, 'current_user': current_user})

    def post(self, request, spotify_id):
        user, current_user, error = self.valid_user(request, spotify_id)
        if error:
            return error

        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', spotify_id=user.spotify_id)

        return render(request, 'edit_profile.html', {'form': form, 'current_user': current_user})

# Show profile
class profile_detail(View):
    def get(self, request, spotify_id):
        current_id = request.session.get("spotify_id")
        current_user = User.objects.filter(spotify_id=current_id).first()
        user = get_object_or_404(User, spotify_id=spotify_id)
        return render(request, 'profile_detail.html', {
            'user': user,
            'current_user': current_user,

        })

# Logout
class spotify_logout(View):
    def get(self, request):
        request.session.flush()
        return redirect('spotify_login')

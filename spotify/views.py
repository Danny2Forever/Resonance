import requests
from django.shortcuts import render
from users.models import User
from django.http import HttpResponse

def top_tracks(request):
    spotify_id = request.session.get('spotify_id')
    if not spotify_id:
        return HttpResponse("Not logged in.", status=403)

    user = User.objects.filter(spotify_id=spotify_id).first()
    if not user or not user.access_token:
        return HttpResponse("Spotify access token missing.", status=403)

    headers = {"Authorization": f"Bearer {user.access_token}"}
    resp = requests.get("https://api.spotify.com/v1/me/top/tracks?limit=10", headers=headers)

    if resp.status_code != 200:
        return HttpResponse(f"Spotify API error: {resp.status_code} - {resp.text}")

    data = resp.json()
    tracks = []
    for item in data.get('items', []):
        tracks.append({
            'name': item['name'],
            'artists': ', '.join([artist['name'] for artist in item['artists']]),
            'album': item['album']['name'],
            'image': item['album']['images'][0]['url'] if item['album']['images'] else None,
            'url': item['external_urls']['spotify'],
        })

    return render(request, 'top_tracks.html', {'tracks': tracks})

from .models import User
from django.shortcuts import redirect

def get_current_user(request):
    ''' Return the current_user for views '''
    spotify_id = request.session.get("spotify_id")
    if spotify_id:
        return User.objects.filter(spotify_id=spotify_id).first()
    return redirect('spotify_login')

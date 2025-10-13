from .models import User

def get_current_user(request):
    """Return the currently logged-in user based for templates"""
    spotify_id = request.session.get("spotify_id")
    if spotify_id:
        return User.objects.filter(spotify_id=spotify_id).first()
    return None

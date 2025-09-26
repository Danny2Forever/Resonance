from .models import User

# context for get current user
def current_user(request):
    spotify_id = request.session.get("spotify_id")
    if spotify_id:
        return {
            "current_user": User.objects.filter(spotify_id=spotify_id).first()
        }
    return {"current_user": None}

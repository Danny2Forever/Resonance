from .models import User

# context for get current user
def current_user(request):
    ''' Return the current_user for templates '''
    spotify_id = request.session.get("spotify_id")
    if spotify_id:
        # print("get success")
        return {
            "current_user": User.objects.filter(spotify_id=spotify_id).first()
        }
    # print("not success")
    return {"current_user": None}

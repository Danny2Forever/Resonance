from django.contrib.auth.backends import BaseBackend
from .models import User
class SpotifyBackend(BaseBackend):

    def authenticate(self, request, user=None):
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
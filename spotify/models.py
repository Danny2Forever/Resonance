from django.db import models
from users.models import User

# music profile cach
class UserMusicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    top_artists = models.JSONField(default=list, blank=True, null=True)
    top_tracks = models.JSONField(default=list, blank=True, null=True)
    genres = models.JSONField(default=list, blank=True, null=True)
    last_refreshed = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"MusicProfile of {self.user.spotify_id}"

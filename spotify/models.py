from django.db import models
from users.models import User

# music profile cach
class UserMusicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="music_profile")
    top_artists = models.JSONField(default=list, blank=True)
    top_tracks = models.JSONField(default=list, blank=True)
    genres = models.JSONField(default=list, blank=True)
    last_refreshed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MusicProfile of {self.user.spotify_id}"

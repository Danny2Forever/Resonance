from django.db import models
from users.models import User

class MutualPlaylist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Swipe(models.Model):
    swiper = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swiper')
    swiped = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swiped')
    action = models.CharField(max_length=255)
    swiped_at = models.DateTimeField(auto_now_add=True)


class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_user2')
    similarity_score = models.FloatField()
    matched_at = models.DateTimeField(auto_now_add=True)
    mutual_playlist = models.ForeignKey(MutualPlaylist, on_delete=models.SET_NULL, null=True, blank=True)

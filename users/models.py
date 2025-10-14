from django.db import models

class User(models.Model):
    spotify_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    profile_picture = models.FileField(upload_to='profile_image/%Y/%m/%d/', blank=True, null=True, default="404.jpg")
    bio = models.TextField(blank=True, null=True)
    favorite_song = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)

    access_token = models.CharField(max_length=500, blank=True, null=True)
    refresh_token = models.CharField(max_length=500, blank=True, null=True)
    token_expires_at = models.DateTimeField(max_length=255, blank=True, null=True)


    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True


    swipes = models.ManyToManyField(
        'self',
        through='matching.Swipe',
        symmetrical=False, # ถ้า A swipe B ไม่ได้หมายความว่า B swipe A
        related_name='swiped_by'
    )

    matches = models.ManyToManyField(
        'self',
        through='matching.Match',
        symmetrical=False,
        related_name='matched_with'
    )

    def __str__(self):
        return self.username

from django.shortcuts import render
from django.db import models
from django.contrib.auth.models import User, Matching

class Chat(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

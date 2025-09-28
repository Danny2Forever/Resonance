from django.shortcuts import render
from django.db import models
from django.contrib.auth.models import User, Matching
from django.views import View

class SendMessageView(View):
    def post(self, request):
        chat = get_object_or_404(Chat, id=chat_id)
        user = request.user

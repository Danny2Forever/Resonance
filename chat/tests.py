from django.test import TestCase
from .models import Chat, Message
from users.models import User
from matching.models import Match

class ChatModelTest(TestCase):
    def test_create_chat(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        match = Match.objects.create(user1=user, user2=user)
        chat = Chat.objects.create(match=match)
        self.assertEqual(chat.match, match)

from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Chat

class IsUserInChat(permissions.BasePermission):
    """
    Custom permission to only allow users of a chat to see or post in it.
    """
    def has_permission(self, request, view):
        chat_id = view.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)
        
        is_in_chat = (
            request.user == chat.match.user1 or 
            request.user == chat.match.user2
        )
        
        return is_in_chat
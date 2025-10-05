# from django.shortcuts import render
# from django.db import models
# from django.contrib.auth.models import User, Matching
# from django.http import JsonResponse
# from .models import Message

# class Chat(models.Model):
#     match = models.OneToOneField(Match, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
import json

from .models import Chat, Message
from users.models import User
from matching.models import Match


# List all messages in a chat
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    messages = chat.messages.order_by("sent_at").values(
        "id", "sender_id", "content", "message_type", "shared_item_id", "sent_at"
    )
    return JsonResponse({"chat_id": chat.id, "messages": list(messages)})


# Send a message in a chat
@csrf_exempt
@require_http_methods(["POST"])
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    try:
        data = json.loads(request.body)
        sender_id = data.get("sender_id")
        content = data.get("content")
        message_type = data.get("message_type", "text")
        shared_item_id = data.get("shared_item_id")

        sender = get_object_or_404(User, id=sender_id)

        message = Message.objects.create(
            chat=chat,
            sender=sender,
            content=content,
            message_type=message_type,
            shared_item_id=shared_item_id,
            sent_at=now(),
        )

        return JsonResponse(
            {
                "id": message.id,
                "chat_id": chat.id,
                "sender_id": sender.id,
                "content": message.content,
                "message_type": message.message_type,
                "shared_item_id": message.shared_item_id,
                "sent_at": message.sent_at,
            },
            status=201,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
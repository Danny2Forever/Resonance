from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from matching.models import Match

# Import our new custom permission
from .permissions import IsUserInChat
from .models import Chat
from .serializers import MessageSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsUserInChat])
def chat_detail(request, chat_id):

    chat = get_object_or_404(Chat, id=chat_id)


    messages = chat.messages.all().order_by('sent_at')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsUserInChat])
def send_message(request, chat_id):

    chat = get_object_or_404(Chat, id=chat_id)
    serializer = MessageSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save(chat=chat, sender=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@login_required
def chat_list_view(request):
    user_matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1', 'user2', 'chat').order_by('-matched_at')

    chat_list = []
    for match in user_matches:
        other_user = match.user2 if match.user1 == request.user else match.user1
        chat_id = match.chat.id if hasattr(match, 'chat') else None
        if chat_id:
            chat_list.append({
                'chat_id': chat_id,
                'other_user': other_user,
            })

    context = {'chat_list': chat_list}
    return render(request, 'chat/chat.html', context)
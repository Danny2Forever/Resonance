from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):

    sender_id = serializers.ReadOnlyField(source='sender.id')

    class Meta:
        model = Message
        fields = [
            'id', 
            'chat', 
            'sender_id',
            'content', 
            'message_type', 
            'shared_item_id', 
            'sent_at'
        ]

        read_only_fields = ['id', 'chat', 'sent_at']


    def validate(self, data):
        """
        Custom validation to ensure that if the message type is 'text',
        the content field is not empty.
        """
        message_type = data.get('message_type', 'text')
        content = data.get('content')

        if message_type == 'text' and not content:
            raise serializers.ValidationError("Content is required for text messages.")

        return data
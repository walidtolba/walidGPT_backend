from rest_framework import serializers
from .models import Session, Message, RecordMessage
from users.serializers import UserSerializer

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class RecordMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordMessage
        fields = '__all__'
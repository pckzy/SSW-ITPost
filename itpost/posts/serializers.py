from rest_framework import serializers
from django.utils.timesince import timesince
from django.utils.timezone import now
from .models import *

class CommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    image = serializers.CharField(source="user.image", read_only=True)
    created_at_human = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user_full_name', 'username', 'content', 'created_at', 'created_at_human', 'image']

    def get_created_at_human(self, obj):
        text = timesince(obj.created_at, now())
        return text.replace('minutes', 'นาที').replace('minute', 'นาที').replace('hours', 'ชม.').replace('hour', 'ชม.').replace('days', 'วัน').replace('day', 'วัน') + 'ที่แล้ว';



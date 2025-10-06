from rest_framework import serializers
from posts.models import Course, Comment, Enrollment
from django import forms
from django.utils.timesince import timesince
from django.utils.timezone import now

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'course_code', 'course_name', 'description', 'allowed_years', 'allowed_majors', 'allowed_specializations',
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_professor = serializers.CharField(source='course.created_by.get_full_name', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'is_approved', 'enrolled_at', 'course_professor']


class CommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    image = serializers.CharField(source="user.profile.image", read_only=True)
    created_at_human = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user_full_name', 'username', 'content', 'created_at', 'created_at_human', 'image']

    def get_created_at_human(self, obj):
        text = timesince(obj.created_at, now())
        return text.replace('minutes', 'นาที').replace('minute', 'นาที').replace('hours', 'ชม.').replace('hour', 'ชม.').replace('days', 'วัน').replace('day', 'วัน') + 'ที่แล้ว';

from rest_framework import serializers
from posts.models import Course, Comment, Enrollment
from django.contrib.auth.models import User, Group
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


class UserCreateSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    group = serializers.ChoiceField(choices=['Admin', 'Professor'], write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'group')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("มีชื่อผู้ใช้นี้อยู่ในระบบแล้ว")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("อีเมลนี้ถูกใช้งานแล้ว")
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": ["รหัสผ่านไม่ตรงกัน"]})
        return attrs

    def create(self, validated_data):
        group_name = validated_data.pop('group')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        user.set_password(validated_data['password1'])
        user.save()

        group = Group.objects.get(name=group_name)
        user.groups.add(group)

        return user

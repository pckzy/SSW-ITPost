from rest_framework import serializers
from posts.models import Course
from django import forms

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'course_code', 'course_name', 'description', 'allowed_years', 'allowed_majors', 'allowed_specializations',
        ]

    # def validate_course_code(self, value):
    #     qs = Course.objects.filter(course_code__iexact=value)
    #     if self.instance and self.instance.pk:
    #         qs = qs.exclude(pk=self.instance.pk)
    #     if qs.exists():
    #         raise serializers.ValidationError("รหัสวิชานี้มีอยู่แล้วในระบบ")
    #     return value



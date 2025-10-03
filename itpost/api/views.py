from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourseSerializer

@api_view(['POST'])
def create_course_api(request):
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        course = serializer.save(created_by=request.user)

        return Response({
            'success': True,
            'course': {
                'id': course.id,
                'title': course.course_name,
                'description': course.description,
                'course_code': course.course_code,
                'student_count': course.students.count() if hasattr(course, 'students') else 0,
                'post_count': course.posts.count() if hasattr(course, 'posts') else 0
            }
        }, status=status.HTTP_201_CREATED)

    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
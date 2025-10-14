from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourseSerializer, CommentSerializer, EnrollmentSerializer, UserCreateSerializer

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404


from posts.models import *

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


class ToggleLikeView(LoginRequiredMixin, APIView):
    def post(self, request, post_id):
        user = request.user
        post = Post.objects.get(pk=post_id)

        if user in post.liked_by.all():
            post.liked_by.remove(user)
            liked = False
        else:
            post.liked_by.add(user)
            liked = True

        return Response({'success': True, 'liked': liked, 'count': post.liked_by.count()})
    

class PostCommentView(LoginRequiredMixin, PermissionRequiredMixin, APIView):
    permission_required = 'posts.view_comment'
    def get(self, request, post_id):
        post = Post.objects.get(pk=post_id)

        comments = Comment.objects.filter(post=post).order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response({
            "success": True,
            "post_title": post.title,
            "comments": serializer.data
        })

    
    def post(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        user = request.user

        comment = Comment.objects.create(
            post=post,
            user=user,
            content=request.data.get("content", "")
        )

        serializer = CommentSerializer(comment)
        return Response({"success": True, "comment": serializer.data}, status=201)
    

class EnrollCourseAPIView(APIView):
    def post(self, request, course_id):
        user = request.user

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        existing = Enrollment.objects.filter(student=user, course=course).first()
        if existing:
            return Response({'success': False, 'message': 'Already Enrolled'}, status=status.HTTP_200_OK)

        enroll = Enrollment.objects.create(student=user, course=course)
        serializer = EnrollmentSerializer(enroll)

        return Response({'success': True, 'message': 'Enrollment request sent', 'enrollment': serializer.data}, status=status.HTTP_201_CREATED)
    
    def put(self, request, course_id):

        try:
            enrollments = Enrollment.objects.get(pk=course_id)
        except Enrollment.DoesNotExist:
            return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        enrollments.is_approved = True
        enrollments.save()

        return Response({'success': True, 'message': 'Enrollment approve sent'}, status=status.HTTP_200_OK)
    
    def delete(self, request, course_id):
        try:
            enrollments = Enrollment.objects.get(pk=course_id)
        except Enrollment.DoesNotExist:
            return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        enrollments.delete()

        return Response({'success': True, 'message': 'Delete Enrollment'}, status=status.HTTP_200_OK)
    

class DeletePostView(LoginRequiredMixin, PermissionRequiredMixin, APIView):
    permission_required = 'posts.delete_post'
    def post(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        post.delete()
        
        return Response({'success': True})
    
class PostApprovalView(LoginRequiredMixin, PermissionRequiredMixin, APIView):
    permission_required = 'posts.change_post'
    def post(self, request, post_id):
        Post.objects.filter(pk=post_id).update(status='approved')
        return Response({'success': True, 'message': 'Post approved'}, status=status.HTTP_200_OK)

class PostRejectView(LoginRequiredMixin, PermissionRequiredMixin, APIView):
    permission_required = 'posts.change_post'
    def post(self, request, post_id):
        Post.objects.filter(pk=post_id).update(status='rejected')
        return Response({'success': True, 'message': 'Post approved'}, status=status.HTTP_200_OK)
    

class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, APIView):
    permission_required = 'auth.add_user'
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            group_name = user.groups.first().name

            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'group': group_name,
                    'count': User.objects.all().count(),
                }
            }, status=status.HTTP_201_CREATED)

        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class DeleteUserView(LoginRequiredMixin, PermissionRequiredMixin, APIView):
    permission_required = 'auth.delete_user'
    def delete(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({'success': True, 'message': 'Delete User'}, status=status.HTTP_200_OK)
    

class CourseView(LoginRequiredMixin, PermissionRequiredMixin, APIView):
    permission_required = 'posts.delete_course'

    def delete(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        course.delete()
        return Response({'success': True, 'message': 'Deleted Course'}, status=status.HTTP_200_OK)
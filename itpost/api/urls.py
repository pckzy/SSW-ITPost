from django.urls import path
from .views import *

urlpatterns = [
    path('courses/create/', create_course_api, name='create-course-api'),
    path("like/<int:post_id>/", ToggleLikeView.as_view(), name="toggle_like"),
    path("comments/<int:post_id>/", PostCommentView.as_view(), name="post_comment"),
    path("enroll_course/<int:course_id>/", EnrollCourseAPIView.as_view(), name="enroll_course_view"),
    path("delete/<int:post_id>/", DeletePostView.as_view(), name="delete_post"),
    path('approve/<int:post_id>/', PostApprovalView.as_view(), name='approve_post'),
    path('reject/<int:post_id>/', PostRejectView.as_view(), name='reject_post'),
    path('user/', UserCreateView.as_view(), name='create_user'),
    path('user/delete/<str:username>', UserDeleteView.as_view(), name='delete_user'),
]
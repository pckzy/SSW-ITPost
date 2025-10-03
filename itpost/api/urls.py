from django.urls import path
from .views import create_course_api

urlpatterns = [
    path('courses/create/', create_course_api, name='create-course-api'),
]
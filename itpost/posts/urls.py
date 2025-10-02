from django.urls import path

from . import views

urlpatterns = [
    path("", views.MainView.as_view(), name="main_view"),
    path("test/", views.test_view, name="test_view"),
    path("back/", views.back, name="back"),
    path("login/", views.LoginView.as_view(), name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("register/", views.RegisterView.as_view(), name="register_view"),
    path("course/<str:course_code>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("manage_course/", views.ManageCourseView.as_view(), name="manage_course_view"),
    path("manage_course/create_posts", views.ProfCreatePostView.as_view(), name="prof_create_post_view"),
    path("manage_course/edit_course/<int:course_id>", views.EditCourseView.as_view(), name="course_edit_view"),
]
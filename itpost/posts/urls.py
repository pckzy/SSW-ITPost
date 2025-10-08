from django.urls import path

from . import views

urlpatterns = [
    path("", views.MainView.as_view(), name="main_view"),
    path("test/", views.test_view, name="test_view"),
    path("back/", views.back, name="back"),
    path("login/", views.LoginView.as_view(), name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("register/", views.RegisterView.as_view(), name="register_view"),
    path("profile/<str:username>/", views.ProfileView.as_view(), name="profile_view"),
    path("profile/edit/<str:username>/", views.EditProfileView.as_view(), name="edit_profile_view"),
    path("student/", views.StudentView.as_view(), name="student_view"),
    path("student/courses/", views.StudentCourseView.as_view(), name="student_course_view"),
    path("student/create_post/", views.StudentCreatePostView.as_view(), name="student_create_post"),
    path("student/edit_post/<int:post_id>/", views.EditPostView.as_view(), name="edit_post_view"),
    path("course/<str:course_code>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("course/<str:course_code>/students/", views.CourseDetailStudentView.as_view(), name="course_detail_student"),
    path("professor/manage_course/", views.ProfManageCourseView.as_view(), name="prof_manage_course_view"),
    path("manage_course/", views.ManageCourseView.as_view(), name="manage_course_view"),
    path("manage_course/create_posts/", views.ProfCreatePostView.as_view(), name="prof_create_post_view"),
    path("manage_course/edit_course/<int:course_id>/", views.EditCourseView.as_view(), name="course_edit_view"),
    path("administrator/", views.AdminView.as_view(), name="admin_view"),
    path("administrator/courses", views.AdminCourseView.as_view(), name="admin_course_view"),
]
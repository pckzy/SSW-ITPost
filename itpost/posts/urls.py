from django.urls import path

from . import views

urlpatterns = [
    path("", views.MainView.as_view(), name="main_view"),
    path("login/", views.LoginView.as_view(), name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("register/", views.RegisterView.as_view(), name="register_view"),
]
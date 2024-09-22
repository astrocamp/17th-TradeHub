from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("", views.index, name="index"),
    path("log_in", views.log_in, name="log_in"),
    path("log_out", views.log_out, name="log_out"),
    path("register", views.register, name="register"),
    path("reset_password", views.reset_password, name="reset_password"),
    path("forget_password", views.forget_password, name="forget_password"),
    path("profile/<int:id>", views.profile, name="profile"),
    path("profile/edit/<int:id>", views.edit_profile, name="edit_profile"),
    path("notifications", views.notifications, name="notifications"),
]

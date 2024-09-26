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
    path("update_company_id", views.update_company_id, name="update_company_id"),
    path("invitation_register/", views.invitation_register, name="invitation_register"),
    path("send-invitation/", views.send_invitation, name="send_invitation"),
    path("notifications", views.notifications, name="notifications"),
    path(
        "notifications/<int:notification_id>/mark_as_read/",
        views.mark_as_read,
        name="mark_as_read",
    ),
    path("notifications/all", views.all_notifications, name="all_notifications"),
    path(
        "notifications/<int:notification_id>/mark_as_read_fullpage/",
        views.mark_as_read_fullpage,
        name="mark_as_read_fullpage",
    ),
    path("notifications/unread_count", views.unread_count, name="unread_count"),
    path("notifications/mark_all_as_read", views.mark_all_as_read, name="mark_all_as_read"),
]

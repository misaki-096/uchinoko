from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("sign_up/", views.SignupView.as_view(), name="sign_up"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("delete/<int:pk>/", views.UserDelete.as_view(), name="delete"),
    path("reset/", views.PasswordReset.as_view(), name="password_reset"),
    path("reset/done/", views.PasswordResetDone.as_view(), name="password_reset_done"),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        views.PasswordResetComplete.as_view(),
        name="password_reset_complete",
    ),
]

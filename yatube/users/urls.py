from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'password_change/',
        views.PasswordChange.as_view(),
        name='password_change'
    ),
    path(
        'password_change/done/',
        views.PasswordChangeDone.as_view(),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        views.PasswordReset.as_view(),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        views.PasswordResetDone.as_view(),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>',
        views.Reset.as_view(),
        name='reset'
    ),
    path(
        'reset/done/',
        views.ResetDone.as_view(),
        name='reset_done'
    ),
]

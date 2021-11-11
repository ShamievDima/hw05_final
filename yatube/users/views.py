from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(CreateView):
    form_class = CreationForm
    template_name = 'users/password_change_form.html'


class PasswordChangeDone(CreateView):
    form_class = CreationForm
    template_name = 'users/password_change_done.html'


class PasswordReset(CreateView):
    form_class = CreationForm
    template_name = 'users/password_reset_form.html'


class PasswordResetDone(CreateView):
    form_class = CreationForm
    template_name = 'users/password_reset_done.html'


class Reset(CreateView):
    form_class = CreationForm
    template_name = 'users/password_reset_confirm.html'


class ResetDone(CreateView):
    form_class = CreationForm
    template_name = 'users/password_reset_complete.html'

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db.models.base import Model as Model
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView

from .forms import LoginForm, ResetForm, SetPassword, SignUpForm
from .models import User


class IndexView(TemplateView):
    template_name = "accounts/index.html"

    def get(self, request):
        if self.request.user.is_authenticated:
            return redirect("app:home")
        else:
            return render(request, self.template_name)


class SignupView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/sign_up.html"
    success_url = reverse_lazy("app:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        user = authenticate(email=email, password=password)
        login(self.request, user)
        return response


class LoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"


class LogoutView(LoginRequiredMixin, LogoutView):
    template_name = "accounts/login.html"


class UserDelete(LoginRequiredMixin, DeleteView):
    template_name = "accounts/user_delete.html"
    model = User
    success_url = reverse_lazy("accounts:index")


class PasswordReset(PasswordResetView):
    form_class = ResetForm
    template_name = "accounts/password_reset_form.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")

    def form_valid(self, form):
        response = super().form_valid(form)
        e = self.request.POST.get("email")
        e_exists = User.objects.filter(email=e).exists()
        if e_exists:
            return response
        else:
            messages.error(self.request, "登録されていないメールアドレスです。")
            return redirect("accounts:password_reset")


class PasswordResetDone(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = SetPassword
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"

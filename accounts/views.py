from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import SignUpForm, LoginForm


class IndexView(TemplateView):
    template_name = "accounts/index.html"

    def get_template_names(self):
        if self.request.user.is_authenticated:
            template_name = "app/home.html"
        else:
            template_name = self.template_name

        return [template_name]


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

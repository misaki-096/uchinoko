from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


# def index(request):
#   return HttpResponse("<h1>Hello World</h1>")
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "app/home.html"

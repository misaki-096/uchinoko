from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = "app"

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path("image/", views.ImageFile.as_view(), name="image"),
    path("search/", views.Search.as_view(), name="search"),
    path("delete/<int:pk>", views.WordDelete.as_view(), name="delete"),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "app"

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path("image/", views.Image.as_view(), name="image"),
    path(
        "image_search/<search_word>/",
        views.ImageSearch.as_view(),
        name="image_search",
    ),
    path(
        "image_search/<search_word>/folder_choice",
        views.FolderChoice.as_view(),
        name="folder_choice",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)

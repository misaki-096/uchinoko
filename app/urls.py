from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "app"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("image", views.ImageView.as_view(), name="image"),
    path("images_list", views.ImagesListView.as_view(), name="images_list"),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)

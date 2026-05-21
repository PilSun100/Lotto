from django.contrib import admin
from django.urls import include, path

from lottery.views import HomeView


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("tickets/", include("lottery.urls")),
]

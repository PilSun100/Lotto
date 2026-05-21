from django.contrib import admin
from django.urls import include, path

from lottery.views import HomeView

admin.site.site_header = "Lotto 관리자"
admin.site.site_title = "Lotto 관리자"
admin.site.index_title = "Lotto 사이트 관리"


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("tickets/", include("lottery.urls")),
]

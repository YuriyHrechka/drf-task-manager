from django.contrib import admin
from django.urls import include, path
from users.views import AuthView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", AuthView.as_view(), name="auth"),
    path("api/", include("tasks.urls")),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

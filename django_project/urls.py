from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("public_app.urls")),
    path("", include("accounts.urls")),
    path("", include("tenant_app.urls")),
]
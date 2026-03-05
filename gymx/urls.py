from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.public_app.urls")),
    path("", include("apps.accounts.urls")),
    path("", include("apps.tenant_app.urls")),
]
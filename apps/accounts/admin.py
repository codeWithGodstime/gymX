from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

# Unregister the default UserAdmin first
admin.site.unregister(CustomUser)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        "email",
        "username",
        "is_staff",
        "is_active",
    ]
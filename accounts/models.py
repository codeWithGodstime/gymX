from django.contrib.auth.models import AbstractUser
from django.db import models
from django_tenants.models import DomainMixin, TenantMixin

class CustomUser(AbstractUser):
    is_gym_admin = models.BooleanField(default=False)

class Gym(TenantMixin):
    name = models.CharField(max_length=100)
    owner = models.OneToOneField(
        CustomUser,  
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    auto_create_schema = True  # ensures schema is created when saving

class Domain(DomainMixin):
    pass
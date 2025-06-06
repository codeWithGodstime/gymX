from django.db import models
from django_tenants.models import DomainMixin, TenantMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    auto_create_schema = True  # ensures schema is created when saving


class Domain(DomainMixin):
    pass
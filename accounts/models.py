from django.contrib.auth.models import AbstractUser
from django.db import models

from public_app.models import Client

class CustomUser(AbstractUser):
    tenant = models.OneToOneField(Client, on_delete=models.CASCADE)


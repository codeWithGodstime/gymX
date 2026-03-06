from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.public_app.models import Gym

class User(AbstractUser):
    tenant = models.OneToOneField(Gym, on_delete=models.CASCADE)
    


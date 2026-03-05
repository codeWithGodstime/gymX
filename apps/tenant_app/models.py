from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Members(models.Model):
    name = models.CharField(max_length=50)
    contact = models.CharField(max_length=16)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    type = models.CharField(max_length=10, choices=[('one-time', 'one-time'), ('monthly', 'monthly')])


class MemberPayment(models.Model):
    date_of_payment = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateField()
    member = models.ForeignKey(Members, on_delete=models.CASCADE, related_name='member_payments')
    is_renewal = models.BooleanField(default=False)


class LandingPageConfig(models.Model):
    tenant = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landing_page_config')
    title = models.CharField(max_length=255)
    welcome_message = models.TextField(blank=True)
    # banner_image = models.ImageField(upload_to='landing_banners/', null=True, blank=True)
    primary_color = models.CharField(max_length=20, default="#000000")
    updated_at = models.DateTimeField(auto_now=True)
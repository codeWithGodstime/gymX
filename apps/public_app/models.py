from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Gym(TenantMixin):
    name = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    plan = models.ForeignKey('SubscriptionPlan', on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True, null=True)

    auto_create_schema = True  # ensures schema is created when saving


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    interval = models.CharField(max_length=20, choices=[('monthly','Monthly'), ('yearly','Yearly')])
    paystack_plan_code = models.CharField(max_length=50, blank=True, null=True)


class Subscription(models.Model):
    tenant = models.ForeignKey(Gym, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=[('active','Active'), ('cancelled','Cancelled')])
    paystack_subscription_code = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)


class Domain(DomainMixin):
    pass
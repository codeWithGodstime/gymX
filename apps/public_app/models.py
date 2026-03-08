from django.db import models
from django_tenants.models import DomainMixin, TenantMixin
from datetime import timedelta
from django.utils import timezone


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
    tenant = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=[('active','Active'), ('cancelled','Cancelled')])
    paystack_subscription_code = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    trial_days = models.PositiveIntegerField(default=14)

    def save(self, *args, **kwargs):
    # Set end_date for trial or new subscription if not already set
        if not self.end_date:
            if self.trial_days > 0:
                self.end_date = timezone.now() + timedelta(days=self.trial_days)
                self.status = 'active'  # Trial is treated as active
            elif self.plan and self.plan.interval:
                # Optional: auto-set end_date for paid plans if not provided
                if self.plan.interval == 'monthly':
                    self.end_date = timezone.now() + timedelta(days=30)
                elif self.plan.interval == 'yearly':
                    self.end_date = timezone.now() + timedelta(days=365)
                self.status = 'active'
        super().save(*args, **kwargs)

    @property
    def days_to_next_billing(self):
        """Return number of full days until trial ends or next billing."""
        if not self.end_date:
            return None
        now = timezone.now()
        delta = self.end_date - now
        return max(delta.days, 0)
    
    @property
    def progress_percent(self):
        if self.is_trial_active:
            days_left = self.days_to_next_billing()
            return ((self.trial_days - days_left) / self.trial_days) * 100
        elif self.is_active_or_trial and self.end_date and self.start_date:
            total_days = (self.end_date - self.start_date).days
            days_left = self.days_to_next_billing()
            return ((total_days - days_left) / total_days) * 100
        return 0

    @property
    def is_trial_active(self):
        return self.trial_days > 0 and timezone.now() <= self.end_date

    @property
    def is_active_or_trial(self):
        return self.status == 'active' or self.is_trial_active

class Domain(DomainMixin):
    pass
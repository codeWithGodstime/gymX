import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()


class Activity(models.Model):

    class ActivityType(models.TextChoices):
        MEMBER_CREATED = "member_created", _("Member Created")
        MEMBER_UPDATED = "member_updated", _("Member Updated")
        MEMBER_DELETED = "member_deleted", _("Member Deleted")

        MEMBER_CHECKIN = "member_checkin", _("Member Checked In")

        PAYMENT_SUCCESS = "payment_success", _("Payment Successful")
        PAYMENT_FAILED = "payment_failed", _("Payment Failed")

        PLAN_CREATED = "plan_created", _("Plan Created")
        PLAN_UPDATED = "plan_updated", _("Plan Updated")

        STAFF_ADDED = "staff_added", _("Staff Added")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities"
    )
    activity_type = models.CharField(
        max_length=50,
        choices=ActivityType.choices
    )
    description = models.TextField(blank=True)
    metadata = models.JSONField(
        blank=True,
        null=True,
        help_text="Extra data related to the activity"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Activities"

    def __str__(self):
        return f"{self.activity_type} - {self.created_at}"


class Member(models.Model):
    """
    Renamed from 'Members' → singular 'Member' (Django convention)
    """
    name = models.CharField(max_length=100)           # increased a bit
    contact = models.CharField(max_length=20)         # phone numbers often need more space
    member_type = models.CharField(                    # renamed 'type' → more descriptive
        max_length=10,
        choices=[
            ('one-time', 'One-time'),
            ('monthly', 'Monthly'),
        ],
        default='monthly',
    )
    created_at = models.DateTimeField(auto_now_add=True)   # better to use DateTimeField
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Member"
        verbose_name_plural = "Members"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.member_type})"

    @property
    def is_active(self):
        """Quick helper to check if membership is currently valid"""
        latest_payment = self.member_payments.order_by('-expiration_date').first()
        if not latest_payment:
            return False
        return latest_payment.expiration_date >= timezone.now().date()


class MemberPayment(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='payments'          # better name than 'member_payments'
    )
    date_of_payment = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateField()
    is_renewal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-date_of_payment']
        get_latest_by = 'expiration_date'

    def __str__(self):
        return f"{self.member.name} - {self.amount} - {self.expiration_date}"


class Attendance(models.Model):
    pass
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


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


class Attendance(models.Model):
    pass
from django.db import models


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
from django import forms
from .models import Members, MemberPayment


class MemberCreationForm(forms.Form):
    name = forms.CharField(max_length=50)
    contact = forms.CharField(max_length=16)
    type = forms.ChoiceField(choices=[('one-time', 'One-time'), ('monthly', 'Monthly')])
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from allauth.account.forms import LoginForm
from .models import CustomUser
from django_tenants.utils import get_public_schema_name
# forms.py
from allauth.account.forms import SignupForm
from django import forms
from django_tenants.utils import tenant_context
from public_app.models import Client, Domain


class GymOwnerSignupForm(SignupForm):
    gym_name = forms.CharField(max_length=100)
    subdomain = forms.CharField(max_length=50)

class CustomUserCreationForm(AdminUserCreationForm):

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
        )


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
        )

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

        self.label_classes = 'form-label'
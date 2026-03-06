from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from allauth.account.forms import LoginForm
from django.contrib.auth import get_user_model
from django_tenants.utils import get_public_schema_name
# forms.py
from allauth.account.forms import SignupForm
from django import forms
from django_tenants.utils import tenant_context
from apps.public_app.models import Gym, Domain


CustomUser = get_user_model()

class GymOwnerSignupForm(SignupForm):
    gym_name = forms.CharField(max_length=100)
    

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
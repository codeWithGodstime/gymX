from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django_tenants.utils import get_public_schema_name
from allauth.account.forms import LoginForm
from .models import CustomUser


# forms.py
from allauth.account.forms import SignupForm
from django import forms
from .models import Gym, Domain
from django_tenants.utils import tenant_context

class GymOwnerSignupForm(SignupForm):
    gym_name = forms.CharField(max_length=100)
    subdomain = forms.CharField(max_length=50)

    def save(self, request):
        print("CALLED")
        user = super().save(request)
        user.is_gym_owner = True
        user.save()

        with tenant_context(Gym.objects.get(schema_name=get_public_schema_name())):
            gym = Gym.objects.create(
                name=self.cleaned_data['gym_name'],
                schema_name=self.cleaned_data['subdomain'],
                owner=user,
            )
            Domain.objects.create(
                domain=f"{self.cleaned_data['subdomain']}.localhost",
                tenant=gym,
                is_primary=True
            )

        return user

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
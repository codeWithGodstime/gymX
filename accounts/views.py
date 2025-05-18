from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django_tenants.utils import tenant_context
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import FormView

from public_app.models import Client, Domain
from .forms import GymOwnerSignupForm

User = get_user_model()


class GymOwnerSignupView(FormView):
    form_class = GymOwnerSignupForm
    template_name = 'account/signup.html'
    success_url = "dashboard"

    def form_valid(self, form, *args, **kwargs):
        tenant = Client.objects.create(
            schema_name=form.cleaned_data['subdomain'],
            name=form.cleaned_data['gym_name']
        )

        Domain.objects.create(
            domain=f"{form.cleaned_data['subdomain']}.{settings.DOMAIN_HOST}",
            tenant=tenant,
            is_primary=True
        )

        User.objects.create_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
            username=form.cleaned_data['gym_name']
        )
        super().form_valid(form, *args, **kwargs)
        tenant_domain = f"{form.cleaned_data['subdomain']}.{settings.DOMAIN_HOST}"
        return redirect(f"http://{tenant_domain}/accounts/login/")
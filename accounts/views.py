from allauth.account.views import SignupView
from django.contrib.auth import get_user_model
from django_tenants.utils import tenant_context
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import GymOwnerSignupForm
from .models import Gym, Domain


User = get_user_model()

class GymOwnerSignupView(SignupView):
    form_class = GymOwnerSignupForm
    template_name = 'account/signup.html' 
    form_class = GymOwnerSignupForm

    def get_context_data(self, **kwargs):
        print("THIS SHOULD")
        context = super().get_context_data(**kwargs)
        context['is_gym_owner_signup'] = True
        return context


        print("CALLED==")
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.is_gym_owner = True 
        user.save()

        gym_name = self.request.POST.get('gym_name')
        subdomain = self.request.POST.get('subdomain')
        
        with tenant_context(Gym.objects.get(schema_name='public')):
            gym = Gym.objects.create(
                name=gym_name,
                schema_name=subdomain,
                owner=user,
                auto_create_schema=True
            )
            Domain.objects.create(
                domain=f"{subdomain}.yourdomain.com",
                tenant=gym,
                is_primary=True
            )

        messages.success(self.request, 'Gym created successfully!')
        return super().form_valid(form)
from django.contrib.auth.forms import UserChangeForm
from allauth.account.forms import LoginForm
from django.contrib.auth import get_user_model
from django_tenants.utils import get_public_schema_name
# forms.py
from allauth.account.forms import SignupForm
from django import forms
from django_tenants.utils import tenant_context
from apps.public_app.models import Gym, Domain


CustomUser = get_user_model()


INPUT_CLASSES = (
    "w-full pl-12 pr-4 h-14 rounded-xl border border-slate-200 dark:border-slate-700 "
    "bg-white dark:bg-slate-800 text-slate-900 dark:text-white "
    "focus:border-primary focus:ring-1 focus:ring-primary transition-all outline-none"
)


class UserSignupForm(SignupForm):
    full_name = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "e.g. Alex Johnson"
        })
    )

    # If you're overriding email (optional – allauth already provides it)
    email = forms.EmailField(
        max_length=255,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "alex@yourgym.com"
        })
    )

    # Password field – overriding to customize appearance
    password1 = forms.CharField(           # ← important: use password1 (allauth naming)
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Min. 8 characters"
        })
    )

    password2 = forms.CharField(           # ← important: use password2
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Confirm your password"
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: if you want to be extra sure allauth's defaults don't override your style
        for field_name in ['email', "full_name", 'password1', 'password2']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({"class": INPUT_CLASSES})
        
        self.fields = {
            'full_name':  self.fields['full_name'],
            'email':      self.fields['email'],
            'password1':  self.fields['password1'],
            'password2':  self.fields['password2'],
            # If you ever add more fields (e.g. username, phone, etc.), put them here
        }

    def save(self, request):
        # Create the user via allauth's machinery
        user = super().save(request)

        user.full_name = self.cleaned_data['full_name']
        user.save()

        return user


class GymOwnerForm(forms.ModelForm):
    
    gym_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 "
                     "text-slate-900 dark:text-slate-100 focus:border-primary focus:ring-primary h-12 px-4 text-base transition-all",
            "placeholder": "e.g. Iron Paradise Fitness"
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 "
                     "text-slate-900 dark:text-slate-100 focus:border-primary focus:ring-primary min-h-24 p-4 text-base transition-all",
            "placeholder": "123 Fitness Ave, Muscle City, NY 10001"
        })
    )
    estimated_members = forms.ChoiceField(
        choices=[
            ("0-50", "0 - 50"),
            ("51-200", "51 - 200"),
            ("201-500", "201 - 500"),
            ("500+", "500+"),
        ],
        widget=forms.Select(attrs={
            "class": "w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 "
                     "text-slate-900 dark:text-slate-100 focus:border-primary focus:ring-primary h-12 px-4 text-base transition-all"
        })
    )
    primary_contact = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 "
                     "text-slate-900 dark:text-slate-100 focus:border-primary focus:ring-primary h-12 px-4 text-base transition-all",
            "placeholder": "+1 (555) 000-0000"
        })
    )
    custom_subdomain = forms.SlugField(
        widget=forms.TextInput(attrs={
            "class": "flex-1 rounded-l-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 "
                     "text-slate-900 dark:text-slate-100 focus:border-primary focus:ring-primary h-12 px-4 text-base text-right transition-all border-r-0",
            "placeholder": "mygym"
        })
    )

    class Meta:
        model = Gym  # Make sure you have a Gym model tied to each tenant
        fields = (
            "gym_name",
            "address",
            "estimated_members",
            "primary_contact",
            "custom_subdomain",
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
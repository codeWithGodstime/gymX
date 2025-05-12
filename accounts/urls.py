from django.urls import path, include
from .views import GymOwnerSignupView


urlpatterns = [
    path('accounts/signup/', GymOwnerSignupView.as_view(), name='account_signup'),
    path("accounts/", include("allauth.urls")),
]
from django.urls import path, include
from .views import GymOwnerSignupView

urlpatterns = [
    path("accounts/signup/", GymOwnerSignupView.as_view()),
    path("accounts/", include("allauth.urls")),
]